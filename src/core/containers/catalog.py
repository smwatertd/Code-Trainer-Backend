from __future__ import annotations

from dependency_injector import containers, providers

from src.core.logger import LoguruLogger
from src.core.settings import AppSettings
from src.features.catalog.services.catalog_service import CatalogService
from src.features.catalog.usecases import CreateTeacherTaskUseCase, GetPublicTaskUseCase, ListPublicTasksUseCase


class CatalogContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)
    uow = providers.Dependency()

    logger = providers.Singleton(LoguruLogger, name="catalog")

    catalog_service = providers.Factory(
        CatalogService,
        uow=uow,
    )

    list_public_tasks_use_case = providers.Factory(
        ListPublicTasksUseCase,
        catalog_service=catalog_service,
    )

    get_public_task_use_case = providers.Factory(
        GetPublicTaskUseCase,
        catalog_service=catalog_service,
    )

    create_teacher_task_use_case = providers.Factory(
        CreateTeacherTaskUseCase,
        catalog_service=catalog_service,
    )
