from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.features.assignment_sets.models import AssignmentSetItemModel, AssignmentSetModel


@dataclass(frozen=True)
class AssignmentSetItemDTO:
    task_id: int
    sort_order: int


@dataclass(frozen=True)
class AssignmentSetDTO:
    id: int
    name: str
    description: str
    teacher_id: int
    visibility: str
    group_id: int | None
    is_archived: bool
    items: tuple[AssignmentSetItemDTO, ...]
    created_at: datetime | None = None
    deadline_at: datetime | None = None


class AssignmentSetRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        name: str,
        description: str,
        teacher_id: int,
        visibility: str,
        group_id: int | None,
        deadline_at: datetime | None = None,
    ) -> AssignmentSetModel:
        row = AssignmentSetModel(
            name=name,
            description=description,
            teacher_id=teacher_id,
            visibility=visibility,
            group_id=group_id,
            deadline_at=deadline_at,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get_by_id(self, set_id: int) -> AssignmentSetModel | None:
        stmt = (
            select(AssignmentSetModel)
            .options(selectinload(AssignmentSetModel.items))
            .where(AssignmentSetModel.id == set_id)
        )
        return await self._session.scalar(stmt)

    async def list_for_teacher(self, teacher_id: int, *, include_archived: bool = False) -> list[AssignmentSetModel]:
        stmt = (
            select(AssignmentSetModel)
            .options(selectinload(AssignmentSetModel.items))
            .where(AssignmentSetModel.teacher_id == teacher_id)
            .order_by(AssignmentSetModel.created_at.desc())
        )
        if not include_archived:
            stmt = stmt.where(AssignmentSetModel.is_archived.is_(False))
        rows = await self._session.scalars(stmt)
        return list(rows.all())

    async def list_public(self) -> list[AssignmentSetModel]:
        stmt = (
            select(AssignmentSetModel)
            .options(selectinload(AssignmentSetModel.items))
            .where(
                AssignmentSetModel.visibility == "public",
                AssignmentSetModel.is_archived.is_(False),
            )
            .order_by(AssignmentSetModel.created_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return list(rows.all())

    async def list_for_groups(self, group_ids: list[int]) -> list[AssignmentSetModel]:
        if not group_ids:
            return []
        stmt = (
            select(AssignmentSetModel)
            .options(selectinload(AssignmentSetModel.items))
            .where(
                AssignmentSetModel.group_id.in_(group_ids),
                AssignmentSetModel.is_archived.is_(False),
            )
            .order_by(AssignmentSetModel.created_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return list(rows.all())

    async def update(
        self,
        row: AssignmentSetModel,
        *,
        name: str | None = None,
        description: str | None = None,
        visibility: str | None = None,
        group_id: int | None = None,
        deadline_at: datetime | None = None,
        is_archived: bool | None = None,
        clear_group: bool = False,
    ) -> AssignmentSetModel:
        if name is not None:
            row.name = name
        if description is not None:
            row.description = description
        if visibility is not None:
            row.visibility = visibility
        if clear_group:
            row.group_id = None
        elif group_id is not None:
            row.group_id = group_id
        if deadline_at is not None:
            row.deadline_at = deadline_at
        if is_archived is not None:
            row.is_archived = is_archived
        await self._session.flush()
        return row

    async def add_item(self, *, set_id: int, task_id: int, sort_order: int) -> AssignmentSetItemModel:
        row = AssignmentSetItemModel(
            assignment_set_id=set_id,
            task_id=task_id,
            sort_order=sort_order,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def remove_item(self, *, set_id: int, task_id: int) -> bool:
        stmt = delete(AssignmentSetItemModel).where(
            AssignmentSetItemModel.assignment_set_id == set_id,
            AssignmentSetItemModel.task_id == task_id,
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0


def to_assignment_set_dto(row: AssignmentSetModel) -> AssignmentSetDTO:
    return AssignmentSetDTO(
        id=row.id,
        name=row.name,
        description=row.description,
        teacher_id=row.teacher_id,
        visibility=row.visibility,
        group_id=row.group_id,
        is_archived=row.is_archived,
        created_at=row.created_at,
        deadline_at=row.deadline_at,
        items=tuple(AssignmentSetItemDTO(task_id=item.task_id, sort_order=item.sort_order) for item in row.items),
    )
