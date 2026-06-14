from __future__ import annotations

from dependency_injector import containers, providers

from src.core.logger import LoguruLogger
from src.features.progress.services.curriculum_progress_service import CurriculumProgressService
from src.features.progress.services.task_curriculum_link_service import TaskCurriculumLinkService
from src.features.progress.services.task_progress_service import TaskProgressService
from src.features.progress.usecases import (
    CreateTaskCurriculumLinkUseCase,
    DeleteTaskCurriculumLinkUseCase,
    GetCurriculumDebugUseCase,
    GetCurriculumValidationUseCase,
    GetLearningConceptProgressUseCase,
    GetTaskCurriculumLinksUseCase,
    GetTaskProgressUseCase,
    UpdateTaskCurriculumLinkUseCase,
    ValidateTaskCurriculumLinkUseCase,
)
from src.shared.curriculum.catalog_service import CurriculumCatalogService


class ProgressContainer(containers.DeclarativeContainer):
    uow = providers.Dependency()
    config = providers.Dependency()

    logger = providers.Singleton(LoguruLogger, name="progress")

    progress_service = providers.Factory(TaskProgressService, uow=uow)
    curriculum_progress_service = providers.Factory(CurriculumProgressService, uow=uow)
    task_curriculum_link_service = providers.Factory(
        TaskCurriculumLinkService,
        uow=uow,
        curriculum_root=config.provided.curriculum_dir,
    )
    curriculum_catalog_service = providers.Factory(
        CurriculumCatalogService,
        curriculum_root=config.provided.curriculum_dir,
    )

    get_task_progress_use_case = providers.Factory(
        GetTaskProgressUseCase,
        progress_service=progress_service,
    )
    get_learning_concept_progress_use_case = providers.Factory(
        GetLearningConceptProgressUseCase,
        curriculum_progress_service=curriculum_progress_service,
    )
    validate_task_curriculum_link_use_case = providers.Factory(
        ValidateTaskCurriculumLinkUseCase,
        link_service=task_curriculum_link_service,
    )
    get_task_curriculum_links_use_case = providers.Factory(
        GetTaskCurriculumLinksUseCase,
        link_service=task_curriculum_link_service,
    )
    create_task_curriculum_link_use_case = providers.Factory(
        CreateTaskCurriculumLinkUseCase,
        link_service=task_curriculum_link_service,
    )
    update_task_curriculum_link_use_case = providers.Factory(
        UpdateTaskCurriculumLinkUseCase,
        link_service=task_curriculum_link_service,
    )
    delete_task_curriculum_link_use_case = providers.Factory(
        DeleteTaskCurriculumLinkUseCase,
        link_service=task_curriculum_link_service,
    )
    get_curriculum_validation_use_case = providers.Factory(
        GetCurriculumValidationUseCase,
        catalog_service=curriculum_catalog_service,
    )
    get_curriculum_debug_use_case = providers.Factory(
        GetCurriculumDebugUseCase,
        catalog_service=curriculum_catalog_service,
    )
