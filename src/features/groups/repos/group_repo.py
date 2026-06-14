from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.groups.models import InvitationCodeModel, StudyGroupModel, group_member_table


@dataclass(frozen=True)
class GroupDTO:
    id: int
    name: str
    teacher_id: int
    created_at: datetime | None
    member_count: int = 0


@dataclass(frozen=True)
class InvitationCodeDTO:
    id: int
    code: str
    group_id: int
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    is_active: bool


class GroupRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, name: str, teacher_id: int) -> StudyGroupModel:
        row = StudyGroupModel(name=name, teacher_id=teacher_id)
        self._session.add(row)
        await self._session.flush()
        return row

    async def get_by_id(self, group_id: int) -> StudyGroupModel | None:
        return await self._session.get(StudyGroupModel, group_id)

    async def list_by_teacher(self, teacher_id: int) -> list[tuple[StudyGroupModel, int]]:
        member_count = (
            select(func.count())
            .select_from(group_member_table)
            .where(group_member_table.c.group_id == StudyGroupModel.id)
            .scalar_subquery()
        )
        stmt = (
            select(StudyGroupModel, member_count.label("member_count"))
            .where(StudyGroupModel.teacher_id == teacher_id)
            .order_by(StudyGroupModel.created_at.desc())
        )
        rows = await self._session.execute(stmt)
        return list(rows.all())

    async def list_for_student(self, student_id: int) -> list[StudyGroupModel]:
        stmt = (
            select(StudyGroupModel)
            .join(group_member_table, group_member_table.c.group_id == StudyGroupModel.id)
            .where(group_member_table.c.student_id == student_id)
            .order_by(StudyGroupModel.created_at.desc())
        )
        rows = await self._session.scalars(stmt)
        return list(rows.all())

    async def is_member(self, group_id: int, student_id: int) -> bool:
        stmt = select(group_member_table.c.student_id).where(
            group_member_table.c.group_id == group_id,
            group_member_table.c.student_id == student_id,
        )
        return (await self._session.scalar(stmt)) is not None

    async def add_member(self, group_id: int, student_id: int) -> None:
        await self._session.execute(
            insert(group_member_table).values(group_id=group_id, student_id=student_id),
        )

    async def list_member_group_ids(self, student_id: int) -> list[int]:
        stmt = select(group_member_table.c.group_id).where(
            group_member_table.c.student_id == student_id,
        )
        rows = await self._session.scalars(stmt)
        return list(rows.all())


class InvitationCodeRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        code: str,
        group_id: int,
        teacher_id: int,
        max_uses: int | None,
        expires_at: datetime | None,
    ) -> InvitationCodeModel:
        row = InvitationCodeModel(
            code=code,
            group_id=group_id,
            teacher_id=teacher_id,
            max_uses=max_uses,
            expires_at=expires_at,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get_by_code(self, code: str) -> InvitationCodeModel | None:
        stmt = select(InvitationCodeModel).where(InvitationCodeModel.code == code.strip().upper())
        return await self._session.scalar(stmt)

    async def increment_use_count(self, invitation_id: int) -> None:
        row = await self._session.get(InvitationCodeModel, invitation_id)
        if row is not None:
            row.use_count += 1
