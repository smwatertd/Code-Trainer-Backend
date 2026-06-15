from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.progress.models import TaskCurriculumLinkModel


class TaskCurriculumLinkRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_primary_by_task_and_language(
        self,
        task_id: int,
        language: str,
    ) -> TaskCurriculumLinkModel | None:
        stmt = select(TaskCurriculumLinkModel).where(
            TaskCurriculumLinkModel.task_id == task_id,
            TaskCurriculumLinkModel.language == language.strip().lower(),
            TaskCurriculumLinkModel.is_primary.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_primary_by_task_id(self, task_id: int) -> TaskCurriculumLinkModel | None:
        stmt = (
            select(TaskCurriculumLinkModel)
            .where(
                TaskCurriculumLinkModel.task_id == task_id,
                TaskCurriculumLinkModel.is_primary.is_(True),
            )
            .order_by(TaskCurriculumLinkModel.id.asc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_learning_concept(
        self,
        *,
        language: str,
        learning_concept_id: str,
    ) -> list[TaskCurriculumLinkModel]:
        stmt = select(TaskCurriculumLinkModel).where(
            TaskCurriculumLinkModel.language == language.strip().lower(),
            TaskCurriculumLinkModel.learning_concept_id == learning_concept_id,
            TaskCurriculumLinkModel.is_primary.is_(True),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_task_id(self, task_id: int) -> list[TaskCurriculumLinkModel]:
        stmt = (
            select(TaskCurriculumLinkModel)
            .where(TaskCurriculumLinkModel.task_id == task_id)
            .order_by(
                TaskCurriculumLinkModel.is_primary.desc(),
                TaskCurriculumLinkModel.created_at.asc(),
                TaskCurriculumLinkModel.id.asc(),
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, link_id: int) -> TaskCurriculumLinkModel | None:
        return await self._session.get(TaskCurriculumLinkModel, link_id)

    async def get_by_task_and_pattern(
        self,
        task_id: int,
        exercise_pattern_id: str,
        *,
        language: str | None = None,
    ) -> TaskCurriculumLinkModel | None:
        stmt = select(TaskCurriculumLinkModel).where(
            TaskCurriculumLinkModel.task_id == task_id,
            TaskCurriculumLinkModel.exercise_pattern_id == exercise_pattern_id,
        )
        if language is not None:
            stmt = stmt.where(TaskCurriculumLinkModel.language == language.strip().lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_primary_for_task(self, task_id: int, language: str | None = None) -> None:
        stmt = select(TaskCurriculumLinkModel).where(
            TaskCurriculumLinkModel.task_id == task_id,
            TaskCurriculumLinkModel.is_primary.is_(True),
        )
        if language is not None:
            stmt = stmt.where(TaskCurriculumLinkModel.language == language.strip().lower())
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        for row in rows:
            row.is_primary = False
        if rows:
            await self._session.flush()

    async def add(self, row: TaskCurriculumLinkModel) -> TaskCurriculumLinkModel:
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def update(
        self,
        link_id: int,
        *,
        is_primary: bool | None = None,
        language: str | None = None,
        learning_concept_id: str | None = None,
        technical_concept_id: str | None = None,
        exercise_pattern_id: str | None = None,
        action: str | None = None,
    ) -> TaskCurriculumLinkModel | None:
        row = await self.get_by_id(link_id)
        if row is None:
            return None
        if is_primary is not None:
            row.is_primary = is_primary
        if language is not None:
            row.language = language
        if learning_concept_id is not None:
            row.learning_concept_id = learning_concept_id
        if technical_concept_id is not None:
            row.technical_concept_id = technical_concept_id
        if exercise_pattern_id is not None:
            row.exercise_pattern_id = exercise_pattern_id
        if action is not None:
            row.action = action
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def delete(self, link_id: int) -> bool:
        row = await self.get_by_id(link_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True
