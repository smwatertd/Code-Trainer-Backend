from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import NotFoundFailure
from src.core.interfaces import UnitOfWork
from src.features.catalog.commands import CreateTeacherTaskCommand, ListTasksCommand
from src.features.catalog.domain.dto import TaskDetailDTO, TaskSummaryDTO
from src.features.catalog.mappers import to_detail, to_internal_detail, to_summary
from src.features.catalog.models import TaskModel
from src.features.catalog.repos.task_repo import TaskRepo


@dataclass
class CatalogService:
    uow: UnitOfWork

    async def list_public_tasks(self, *, filters: ListTasksCommand | None = None) -> AppResult[list[TaskSummaryDTO]]:
        async with self.uow(autocommit=False):
            repo = TaskRepo(self.uow.session)
            models = await repo.list_public()
            summaries = [to_summary(model) for model in models]
            if filters is not None:
                summaries = self._apply_filters(summaries, models, filters)
            return Ok(summaries)

    @staticmethod
    def _apply_filters(
        summaries: list[TaskSummaryDTO],
        models: list[TaskModel],
        filters: ListTasksCommand,
    ) -> list[TaskSummaryDTO]:
        model_by_id = {model.id: model for model in models}
        filtered: list[TaskSummaryDTO] = []
        for summary in summaries:
            if filters.difficulty and summary.difficulty != filters.difficulty:
                continue
            if filters.task_type and summary.task_type != filters.task_type:
                continue
            if filters.topic and filters.topic not in summary.topics:
                continue
            filtered.append(summary)
        return filtered

    async def create_teacher_task(self, command: CreateTeacherTaskCommand) -> AppResult[TaskDetailDTO]:
        async with self.uow(autocommit=True):
            repo = TaskRepo(self.uow.session)
            model = await repo.create(
                title=command.title,
                description=command.description,
                difficulty=command.difficulty,
                task_type=command.task_type,
                payload=command.payload,
                owner_user_id=command.owner_user_id,
            )
            return Ok(to_internal_detail(model))

    async def get_public_task(self, task_id: int) -> AppResult[TaskDetailDTO]:
        async with self.uow(autocommit=False):
            repo = TaskRepo(self.uow.session)
            model = await repo.get_public(task_id)
            if not model:
                return Err(NotFoundFailure("Task", str(task_id)))
            return Ok(to_detail(model))

    async def get_internal_task(self, task_id: int) -> AppResult[TaskDetailDTO]:
        async with self.uow(autocommit=False):
            repo = TaskRepo(self.uow.session)
            model = await repo.get_by_id(task_id)
            if not model or model.visibility != "public" or model.is_deleted:
                return Err(NotFoundFailure("Task", str(task_id)))
            return Ok(to_internal_detail(model))
