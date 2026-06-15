from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ForbiddenFailure, NotFoundFailure
from src.core.interfaces import UnitOfWork
from src.features.catalog.commands import (
    CreateTeacherTaskCommand,
    GetTeacherTaskCommand,
    ListTasksCommand,
    ListTeacherTasksCommand,
    UpdateTeacherTaskCommand,
)
from src.features.catalog.domain.dto import TaskDetailDTO, TaskSummaryDTO
from src.features.catalog.mappers import to_detail, to_internal_detail, to_summary
from src.features.catalog.models import TaskModel
from src.features.catalog.repos.task_repo import TaskRepo
from src.features.progress.repos.task_progress_repo import TaskProgressRepo
from src.features.progress.services.task_progress_service import (
    PROGRESS_STATUS_NOT_STARTED,
    progress_status_from_row,
)


@dataclass
class CatalogService:
    uow: UnitOfWork

    async def list_public_tasks(
        self,
        *,
        filters: ListTasksCommand | None = None,
        user_id: int | None = None,
    ) -> AppResult[list[TaskSummaryDTO]]:
        async with self.uow(autocommit=False):
            repo = TaskRepo(self.uow.session)
            models = await repo.list_public()
            summaries = [to_summary(model) for model in models]
            if filters is not None:
                summaries = self._apply_filters(summaries, models, filters)
            if user_id is not None:
                progress_rows = await TaskProgressRepo(self.uow.session).list_by_user(user_id)
                progress_by_task = {
                    row.task_id: progress_status_from_row(row) for row in progress_rows
                }
                summaries = [
                    TaskSummaryDTO(
                        id=item.id,
                        title=item.title,
                        description=item.description,
                        difficulty=item.difficulty,
                        task_type=item.task_type,
                        topics=item.topics,
                        languages=item.languages,
                        progress_status=progress_by_task.get(item.id, PROGRESS_STATUS_NOT_STARTED),
                    )
                    for item in summaries
                ]
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

    async def list_teacher_tasks(self, command: ListTeacherTasksCommand) -> AppResult[list[TaskSummaryDTO]]:
        async with self.uow(autocommit=False):
            repo = TaskRepo(self.uow.session)
            models = await repo.list_by_owner(command.owner_user_id)
            return Ok([to_summary(model) for model in models])

    @staticmethod
    def _can_manage_task(model: TaskModel, *, user_id: int, is_admin: bool) -> bool:
        if is_admin:
            return True
        return model.owner_user_id == user_id

    async def get_teacher_task(self, command: GetTeacherTaskCommand) -> AppResult[TaskDetailDTO]:
        async with self.uow(autocommit=False):
            repo = TaskRepo(self.uow.session)
            model = await repo.get_by_id(command.task_id)
            if not model or model.is_deleted:
                return Err(NotFoundFailure("Task", str(command.task_id)))
            if not self._can_manage_task(model, user_id=command.user_id, is_admin=command.is_admin):
                return Err(ForbiddenFailure("You cannot access this task"))
            return Ok(to_internal_detail(model))

    async def update_teacher_task(self, command: UpdateTeacherTaskCommand) -> AppResult[TaskDetailDTO]:
        async with self.uow(autocommit=True):
            repo = TaskRepo(self.uow.session)
            model = await repo.get_by_id(command.task_id)
            if not model or model.is_deleted:
                return Err(NotFoundFailure("Task", str(command.task_id)))
            if not self._can_manage_task(model, user_id=command.user_id, is_admin=command.is_admin):
                return Err(ForbiddenFailure("You cannot edit this task"))
            if command.title is not None:
                model.title = command.title
            if command.description is not None:
                model.description = command.description
            if command.difficulty is not None:
                model.difficulty = command.difficulty
            if command.payload is not None:
                model.payload = command.payload
            await self.uow.session.flush()
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
