from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.progress.models import StudentCurriculumProgressModel


class CurriculumProgressRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_and_task(self, user_id: int, task_id: int) -> StudentCurriculumProgressModel | None:
        stmt = select(StudentCurriculumProgressModel).where(
            StudentCurriculumProgressModel.user_id == user_id,
            StudentCurriculumProgressModel.task_id == task_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user_tasks(
        self,
        user_id: int,
        task_ids: list[int],
    ) -> list[StudentCurriculumProgressModel]:
        if not task_ids:
            return []
        stmt = select(StudentCurriculumProgressModel).where(
            StudentCurriculumProgressModel.user_id == user_id,
            StudentCurriculumProgressModel.task_id.in_(task_ids),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, row: StudentCurriculumProgressModel) -> StudentCurriculumProgressModel:
        self._session.add(row)
        await self._session.flush()
        return row
