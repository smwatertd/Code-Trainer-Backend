from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.catalog.models import TaskModel


class TaskRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_public(self) -> list[TaskModel]:
        stmt = (
            select(TaskModel)
            .where(
                TaskModel.visibility == "public",
                TaskModel.is_deleted.is_(False),
                TaskModel.workflow_status == "active",
            )
            .order_by(TaskModel.id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_public(self, task_id: int) -> TaskModel | None:
        stmt = select(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.visibility == "public",
            TaskModel.is_deleted.is_(False),
            TaskModel.workflow_status == "active",
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, task_id: int) -> TaskModel | None:
        stmt = select(TaskModel).where(TaskModel.id == task_id, TaskModel.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        title: str,
        description: str,
        difficulty: str,
        task_type: str,
        payload: dict,
        owner_user_id: int | None = None,
        visibility: str = "public",
    ) -> TaskModel:
        model = TaskModel(
            title=title,
            description=description,
            difficulty=difficulty,
            task_type=task_type,
            payload=payload,
            owner_user_id=owner_user_id,
            visibility=visibility,
            workflow_status="active",
            is_deleted=False,
        )
        self._session.add(model)
        await self._session.flush()
        return model
