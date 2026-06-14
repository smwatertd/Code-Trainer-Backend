from __future__ import annotations

from dependency_injector import containers, providers

from src.core.containers.assignment_sets import AssignmentSetsContainer
from src.core.containers.auth import AuthContainer
from src.core.containers.catalog import CatalogContainer
from src.core.containers.db import DBContainer
from src.core.containers.demo import DemoContainer
from src.core.containers.execution import ExecutionContainer
from src.core.containers.groups import GroupsContainer
from src.core.containers.health import HealthContainer
from src.core.containers.languages import LanguagesContainer
from src.core.containers.progress import ProgressContainer
from src.core.containers.submissions import SubmissionsContainer
from src.core.logger import LoguruLogger
from src.core.settings import AppSettings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.features.health.router",
            "src.features.languages.router",
            "src.features.catalog.router",
            "src.features.demo.router",
            "src.features.auth.router",
            "src.features.auth.dependencies",
            "src.features.submissions.router",
            "src.features.progress.router",
            "src.features.progress.curriculum_link_router",
            "src.features.groups.router",
            "src.features.assignment_sets.router",
        ],
    )

    config = providers.Singleton(AppSettings)

    logger = providers.Singleton(LoguruLogger, name="core")

    db = providers.Container(DBContainer, config=config)

    languages = providers.Container(LanguagesContainer)

    execution = providers.Container(
        ExecutionContainer,
        config=config,
        registry=languages.registry,
    )

    catalog = providers.Container(
        CatalogContainer,
        config=config,
        uow=db.uow,
    )

    demo = providers.Container(
        DemoContainer,
        config=config,
        catalog_service=catalog.catalog_service,
        execution_service=execution.execution_service,
    )

    auth = providers.Container(
        AuthContainer,
        config=config,
        uow=db.uow,
    )

    progress = providers.Container(
        ProgressContainer,
        config=config,
        uow=db.uow,
    )

    groups = providers.Container(
        GroupsContainer,
        uow=db.uow,
    )

    assignment_sets = providers.Container(
        AssignmentSetsContainer,
        uow=db.uow,
        group_service=groups.group_service,
    )

    submissions = providers.Container(
        SubmissionsContainer,
        config=config,
        uow=db.uow,
        catalog_service=catalog.catalog_service,
        execution_service=execution.execution_service,
        progress_service=progress.progress_service,
        curriculum_progress_service=progress.curriculum_progress_service,
    )

    health = providers.Container(
        HealthContainer,
        config=config,
        database=db.db,
    )
