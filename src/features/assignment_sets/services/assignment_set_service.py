from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ConflictFailure, ForbiddenFailure, NotFoundFailure, ValidationFailure
from src.core.interfaces import UnitOfWork
from src.features.assignment_sets.repos.assignment_set_repo import (
    AssignmentSetDTO,
    AssignmentSetRepo,
    to_assignment_set_dto,
)
from src.features.catalog.repos.task_repo import TaskRepo
from src.features.groups.services.group_service import GroupService

VALID_VISIBILITIES = frozenset({"public", "private"})


@dataclass
class AssignmentSetService:
    uow: UnitOfWork
    group_service: GroupService

    async def create_set(
        self,
        *,
        teacher_id: int,
        name: str,
        description: str,
        visibility: str,
        group_id: int | None,
        deadline_at: datetime | None = None,
    ) -> AppResult[AssignmentSetDTO]:
        cleaned = name.strip()
        if not cleaned:
            return Err(ValidationFailure("Assignment set name is required"))
        if visibility not in VALID_VISIBILITIES:
            return Err(ValidationFailure("visibility must be public or private"))
        if group_id is not None and not await self.group_service.group_owned_by_teacher(
            group_id,
            teacher_id,
        ):
            return Err(NotFoundFailure("Group", str(group_id)))

        async with self.uow(autocommit=True) as uow:
            row = await AssignmentSetRepo(uow.session).create(
                name=cleaned,
                description=description,
                teacher_id=teacher_id,
                visibility=visibility,
                group_id=group_id,
                deadline_at=deadline_at,
            )
            await uow.session.refresh(row, attribute_names=["items"])
            return Ok(to_assignment_set_dto(row))

    async def list_teacher_sets(
        self,
        teacher_id: int,
        *,
        include_archived: bool = False,
    ) -> AppResult[list[AssignmentSetDTO]]:
        async with self.uow() as uow:
            rows = await AssignmentSetRepo(uow.session).list_for_teacher(
                teacher_id,
                include_archived=include_archived,
            )
            return Ok([to_assignment_set_dto(row) for row in rows])

    async def list_accessible_sets(self, *, user_id: int) -> AppResult[list[AssignmentSetDTO]]:
        group_ids = await self.group_service.student_group_ids(user_id)
        async with self.uow() as uow:
            repo = AssignmentSetRepo(uow.session)
            by_id: dict[int, AssignmentSetDTO] = {}

            for row in await repo.list_public():
                by_id[row.id] = to_assignment_set_dto(row)

            for row in await repo.list_for_groups(group_ids):
                by_id[row.id] = to_assignment_set_dto(row)

            return Ok(list(by_id.values()))

    async def get_set(self, *, user_id: int, role: str, set_id: int) -> AppResult[AssignmentSetDTO]:
        group_ids = await self.group_service.student_group_ids(user_id)
        async with self.uow() as uow:
            row = await AssignmentSetRepo(uow.session).get_by_id(set_id)
            if row is None:
                return Err(NotFoundFailure("AssignmentSet", str(set_id)))
            if not self._can_access_set(user_id=user_id, role=role, row=row, group_ids=group_ids):
                return Err(ForbiddenFailure("Access denied to assignment set"))
            return Ok(to_assignment_set_dto(row))

    async def update_set(
        self,
        *,
        teacher_id: int,
        set_id: int,
        name: str | None = None,
        description: str | None = None,
        visibility: str | None = None,
        group_id: int | None = None,
        clear_group: bool = False,
        deadline_at: datetime | None = None,
        is_archived: bool | None = None,
    ) -> AppResult[AssignmentSetDTO]:
        if visibility is not None and visibility not in VALID_VISIBILITIES:
            return Err(ValidationFailure("visibility must be public or private"))
        if group_id is not None and not await self.group_service.group_owned_by_teacher(
            group_id,
            teacher_id,
        ):
            return Err(NotFoundFailure("Group", str(group_id)))

        async with self.uow(autocommit=True) as uow:
            repo = AssignmentSetRepo(uow.session)
            row = await repo.get_by_id(set_id)
            if row is None or row.teacher_id != teacher_id:
                return Err(NotFoundFailure("AssignmentSet", str(set_id)))

            row = await repo.update(
                row,
                name=name.strip() if name is not None else None,
                description=description,
                visibility=visibility,
                group_id=group_id,
                clear_group=clear_group,
                deadline_at=deadline_at,
                is_archived=is_archived,
            )
            await uow.session.refresh(row, attribute_names=["items"])
            return Ok(to_assignment_set_dto(row))

    async def add_item(
        self,
        *,
        teacher_id: int,
        set_id: int,
        task_id: int,
        sort_order: int | None = None,
    ) -> AppResult[None]:
        async with self.uow(autocommit=True) as uow:
            repo = AssignmentSetRepo(uow.session)
            row = await repo.get_by_id(set_id)
            if row is None or row.teacher_id != teacher_id:
                return Err(NotFoundFailure("AssignmentSet", str(set_id)))
            if await TaskRepo(uow.session).get_by_id(task_id) is None:
                return Err(NotFoundFailure("Task", str(task_id)))

            order = sort_order if sort_order is not None else len(row.items)
            try:
                await repo.add_item(set_id=set_id, task_id=task_id, sort_order=order)
            except IntegrityError:
                return Err(ConflictFailure("Task already in assignment set"))
            return Ok(None)

    async def remove_item(self, *, teacher_id: int, set_id: int, task_id: int) -> AppResult[None]:
        async with self.uow(autocommit=True) as uow:
            repo = AssignmentSetRepo(uow.session)
            row = await repo.get_by_id(set_id)
            if row is None or row.teacher_id != teacher_id:
                return Err(NotFoundFailure("AssignmentSet", str(set_id)))
            removed = await repo.remove_item(set_id=set_id, task_id=task_id)
            if not removed:
                return Err(NotFoundFailure("AssignmentSetItem", str(task_id)))
            return Ok(None)

    def _can_access_set(self, *, user_id: int, role: str, row, group_ids: list[int]) -> bool:
        if row.teacher_id == user_id:
            return True
        if row.is_archived:
            return False
        if row.visibility == "public":
            return True
        if row.group_id is not None and row.group_id in group_ids:
            return True
        return False
