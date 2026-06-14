from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Ok
from src.features.progress.commands import (
    CreateTaskCurriculumLinkCommand,
    DeleteTaskCurriculumLinkCommand,
    GetCurriculumDebugCommand,
    GetCurriculumValidationCommand,
    GetLearningConceptProgressCommand,
    GetTaskCurriculumLinksCommand,
    GetTaskProgressCommand,
    UpdateTaskCurriculumLinkCommand,
    ValidateTaskCurriculumLinkCommand,
)
from src.features.progress.domain.dto import LearningConceptProgressDTO, TaskProgressDTO
from src.features.progress.services.curriculum_progress_service import CurriculumProgressService
from src.features.progress.services.task_curriculum_link_service import (
    TaskCurriculumLinkDTO,
    TaskCurriculumLinkService,
    TaskCurriculumMetadataDTO,
)
from src.features.progress.services.task_progress_service import TaskProgressService
from src.shared.curriculum.catalog_service import CurriculumCatalogService
from src.shared.curriculum.link_validator import CurriculumLinkMetadata


@dataclass
class GetTaskProgressUseCase:
    progress_service: TaskProgressService

    async def execute(self, command: GetTaskProgressCommand) -> AppResult[TaskProgressDTO]:
        progress = await self.progress_service.get_progress_for_task(
            user_id=command.user_id,
            task_id=command.task_id,
        )
        return Ok(progress)


@dataclass
class GetLearningConceptProgressUseCase:
    curriculum_progress_service: CurriculumProgressService

    async def execute(self, command: GetLearningConceptProgressCommand) -> AppResult[LearningConceptProgressDTO]:
        progress = await self.curriculum_progress_service.get_learning_concept_progress(
            user_id=command.user_id,
            language=command.language,
            learning_concept_id=command.learning_concept_id,
        )
        return Ok(progress)


@dataclass
class ValidateTaskCurriculumLinkUseCase:
    link_service: TaskCurriculumLinkService

    async def execute(self, command: ValidateTaskCurriculumLinkCommand) -> AppResult[CurriculumLinkMetadata]:
        return await self.link_service.validate_link_metadata(
            language=command.language,
            technical_concept_id=command.technical_concept_id,
            exercise_pattern_id=command.exercise_pattern_id,
        )


@dataclass
class GetTaskCurriculumLinksUseCase:
    link_service: TaskCurriculumLinkService

    async def execute(self, command: GetTaskCurriculumLinksCommand) -> AppResult[TaskCurriculumMetadataDTO]:
        return await self.link_service.get_task_metadata(command.task_id)


@dataclass
class CreateTaskCurriculumLinkUseCase:
    link_service: TaskCurriculumLinkService

    async def execute(self, command: CreateTaskCurriculumLinkCommand) -> AppResult[TaskCurriculumLinkDTO]:
        return await self.link_service.create_link(
            task_id=command.task_id,
            language=command.language,
            technical_concept_id=command.technical_concept_id,
            exercise_pattern_id=command.exercise_pattern_id,
            is_primary=command.is_primary,
        )


@dataclass
class UpdateTaskCurriculumLinkUseCase:
    link_service: TaskCurriculumLinkService

    async def execute(self, command: UpdateTaskCurriculumLinkCommand) -> AppResult[TaskCurriculumLinkDTO]:
        return await self.link_service.update_link(
            task_id=command.task_id,
            link_id=command.link_id,
            language=command.language,
            technical_concept_id=command.technical_concept_id,
            exercise_pattern_id=command.exercise_pattern_id,
            is_primary=command.is_primary,
        )


@dataclass
class DeleteTaskCurriculumLinkUseCase:
    link_service: TaskCurriculumLinkService

    async def execute(self, command: DeleteTaskCurriculumLinkCommand) -> AppResult[None]:
        return await self.link_service.delete_link(task_id=command.task_id, link_id=command.link_id)


@dataclass
class GetCurriculumValidationUseCase:
    catalog_service: CurriculumCatalogService

    async def execute(self, command: GetCurriculumValidationCommand) -> AppResult[dict]:
        return self.catalog_service.validate_curriculum(command.language)


@dataclass
class GetCurriculumDebugUseCase:
    catalog_service: CurriculumCatalogService

    async def execute(self, command: GetCurriculumDebugCommand) -> AppResult[dict]:
        return self.catalog_service.get_debug_view(command.language)
