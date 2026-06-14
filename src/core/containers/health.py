from __future__ import annotations

from dependency_injector import containers, providers

from src.core.settings import AppSettings
from src.features.health.services.health_service import HealthService
from src.shared.database.database import SqlAlchemyDatabase


class HealthContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)
    database = providers.Dependency(instance_of=SqlAlchemyDatabase)

    health_service = providers.Factory(
        HealthService,
        settings=config,
        database=database,
    )
