from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import NotFoundFailure
from src.core.interfaces import UnitOfWork
from src.features.assignment_sets.models import AssignmentSetItemModel, AssignmentSetModel
from src.features.auth.models import UserModel
from src.features.groups.models import group_member_table
from src.features.groups.repos.group_repo import GroupDTO, GroupRepo
from src.features.progress.models import TaskProgressModel
from src.features.progress.services.task_progress_service import (
    PROGRESS_STATUS_PASSED,
    progress_status_from_row,
)


@dataclass(frozen=True)
class GroupMemberDTO:
    id: int
    name: str
    email: str


@dataclass(frozen=True)
class GroupAssignmentSetSummaryDTO:
    id: int
    name: str
    task_count: int
    deadline_at: datetime | None


@dataclass(frozen=True)
class StudentTaskProgressDTO:
    student_id: int
    task_id: int
    progress_status: str
    attempts_count: int


@dataclass(frozen=True)
class GroupStudentSummaryDTO:
    student_id: int
    student_name: str
    solved_count: int
    total_tasks: int
    progress_percent: float


@dataclass(frozen=True)
class GroupDashboardDTO:
    group: GroupDTO
    members: tuple[GroupMemberDTO, ...]
    assignment_sets: tuple[GroupAssignmentSetSummaryDTO, ...]
    student_summaries: tuple[GroupStudentSummaryDTO, ...]
    task_progress: tuple[StudentTaskProgressDTO, ...]


class GroupDashboardRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_members(self, group_id: int) -> list[GroupMemberDTO]:
        stmt = (
            select(UserModel.id, UserModel.name, UserModel.email)
            .join(group_member_table, group_member_table.c.student_id == UserModel.id)
            .where(group_member_table.c.group_id == group_id)
            .order_by(UserModel.name)
        )
        rows = await self._session.execute(stmt)
        return [GroupMemberDTO(id=row.id, name=row.name, email=row.email) for row in rows.all()]

    async def list_group_assignment_sets(self, group_id: int) -> list[AssignmentSetModel]:
        stmt = (
            select(AssignmentSetModel)
            .where(
                AssignmentSetModel.group_id == group_id,
                AssignmentSetModel.is_archived.is_(False),
            )
            .order_by(AssignmentSetModel.name)
        )
        rows = await self._session.scalars(stmt)
        return list(rows.all())

    async def list_set_task_ids(self, set_id: int) -> list[int]:
        stmt = (
            select(AssignmentSetItemModel.task_id)
            .where(AssignmentSetItemModel.assignment_set_id == set_id)
            .order_by(AssignmentSetItemModel.sort_order)
        )
        rows = await self._session.scalars(stmt)
        return list(rows.all())

    async def get_progress_map(
        self,
        *,
        student_ids: list[int],
        task_ids: list[int],
    ) -> dict[tuple[int, int], TaskProgressModel]:
        if not student_ids or not task_ids:
            return {}
        stmt = select(TaskProgressModel).where(
            TaskProgressModel.user_id.in_(student_ids),
            TaskProgressModel.task_id.in_(task_ids),
        )
        rows = await self._session.scalars(stmt)
        return {(row.user_id, row.task_id): row for row in rows.all()}


@dataclass
class GroupDashboardService:
    uow: UnitOfWork

    async def get_dashboard(self, *, teacher_id: int, group_id: int) -> AppResult[GroupDashboardDTO]:
        async with self.uow() as uow:
            group = await GroupRepo(uow.session).get_by_id(group_id)
            if group is None or group.teacher_id != teacher_id:
                return Err(NotFoundFailure("Group", str(group_id)))

            repo = GroupDashboardRepo(uow.session)
            members = await repo.list_members(group_id)
            sets = await repo.list_group_assignment_sets(group_id)

            all_task_ids: set[int] = set()
            set_summaries: list[GroupAssignmentSetSummaryDTO] = []
            for row in sets:
                task_ids = await repo.list_set_task_ids(row.id)
                all_task_ids.update(task_ids)
                set_summaries.append(
                    GroupAssignmentSetSummaryDTO(
                        id=row.id,
                        name=row.name,
                        task_count=len(task_ids),
                        deadline_at=row.deadline_at,
                    ),
                )

            student_ids = [member.id for member in members]
            progress_map = await repo.get_progress_map(
                student_ids=student_ids,
                task_ids=list(all_task_ids),
            )

            task_progress_rows: list[StudentTaskProgressDTO] = []
            summaries: list[GroupStudentSummaryDTO] = []
            task_list = sorted(all_task_ids)

            for member in members:
                solved = 0
                for task_id in task_list:
                    progress_row = progress_map.get((member.id, task_id))
                    status = progress_status_from_row(progress_row)
                    attempts = progress_row.attempts_count if progress_row else 0
                    if status == PROGRESS_STATUS_PASSED:
                        solved += 1
                    task_progress_rows.append(
                        StudentTaskProgressDTO(
                            student_id=member.id,
                            task_id=task_id,
                            progress_status=status,
                            attempts_count=attempts,
                        ),
                    )
                total = len(task_list)
                pct = round(100.0 * solved / total, 1) if total else 0.0
                summaries.append(
                    GroupStudentSummaryDTO(
                        student_id=member.id,
                        student_name=member.name,
                        solved_count=solved,
                        total_tasks=total,
                        progress_percent=pct,
                    ),
                )

            return Ok(
                GroupDashboardDTO(
                    group=GroupDTO(
                        id=group.id,
                        name=group.name,
                        teacher_id=group.teacher_id,
                        created_at=group.created_at,
                        member_count=len(members),
                    ),
                    members=tuple(members),
                    assignment_sets=tuple(set_summaries),
                    student_summaries=tuple(summaries),
                    task_progress=tuple(task_progress_rows),
                ),
            )
