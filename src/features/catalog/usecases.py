from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.catalog.commands import CreateTeacherTaskCommand, GetTaskCommand, ListTasksCommand
from src.features.catalog.domain.dto import TaskDetailDTO, TaskSummaryDTO
from src.features.catalog.services.catalog_service import CatalogService


@dataclass
class ListPublicTasksUseCase:
    catalog_service: CatalogService

    async def execute(self, command: ListTasksCommand) -> AppResult[list[TaskSummaryDTO]]:
        return await self.catalog_service.list_public_tasks(filters=command, user_id=command.user_id)


@dataclass
class CreateTeacherTaskUseCase:
    catalog_service: CatalogService

    async def execute(self, command: CreateTeacherTaskCommand) -> AppResult[TaskDetailDTO]:
        return await self.catalog_service.create_teacher_task(command)


@dataclass
class GetPublicTaskUseCase:
    catalog_service: CatalogService

    async def execute(self, command: GetTaskCommand) -> AppResult[TaskDetailDTO]:
        return await self.catalog_service.get_public_task(command.task_id)
