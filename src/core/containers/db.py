from __future__ import annotations

from dependency_injector import containers, providers

from src.core.settings import AppSettings
from src.shared.database.database import SqlAlchemyDatabase
from src.shared.database.uow import SqlAlchemyUnitOfWork


class DBContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)

    db = providers.Singleton(SqlAlchemyDatabase, settings=config.provided.db)
    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=db.provided.session_factory,
    )
