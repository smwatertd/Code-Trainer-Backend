from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.interfaces import Database
from src.core.settings import DBSettings
from src.shared.database.base import configure_search_path


class SqlAlchemyDatabase(Database):
    def __init__(self, settings: DBSettings) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=str(settings.dsn),
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            echo=settings.echo,
        )
        configure_search_path(self._engine, settings.db_schema)
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
