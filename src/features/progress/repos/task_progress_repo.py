from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.progress.models import TaskProgressModel


class TaskProgressRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_and_task(self, user_id: int, task_id: int) -> TaskProgressModel | None:
        stmt = select(TaskProgressModel).where(
            TaskProgressModel.user_id == user_id,
            TaskProgressModel.task_id == task_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[TaskProgressModel]:
        stmt = select(TaskProgressModel).where(TaskProgressModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, row: TaskProgressModel) -> TaskProgressModel:
        self._session.add(row)
        await self._session.flush()
        return row
