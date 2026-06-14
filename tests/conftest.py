from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.core.settings import AppSettings, get_settings
from src.shared.database.base import configure_search_path


@pytest.fixture(scope="session")
def settings() -> AppSettings:
    get_settings.cache_clear()
    return AppSettings(_env_file=".env.test")  # type: ignore[call-arg]


@pytest_asyncio.fixture(scope="session")
async def engine(settings: AppSettings) -> AsyncGenerator[AsyncEngine, Any]:
    schema = settings.db.db_schema

    os.environ["DB__NAME"] = settings.db.name
    os.environ["DB__HOST"] = settings.db.host
    os.environ["DB__PORT"] = str(settings.db.port)
    os.environ["DB__USER"] = settings.db.user
    os.environ["DB__PASSWORD"] = settings.db.password
    os.environ["DB__DIALECT"] = settings.db.dialect
    os.environ["DB__DB_SCHEMA"] = schema
    get_settings.cache_clear()

    engine = create_async_engine(
        settings.db.dsn,
        echo=settings.db.echo,
    )
    configure_search_path(engine, schema)

    async with engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await conn.execute(text(f'CREATE SCHEMA "{schema}"'))

    alembic_cfg = Config("alembic.ini")
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    yield engine

    async with engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await conn.execute(text(f'CREATE SCHEMA "{schema}"'))

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session_factory(engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            yield async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )
            await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, Any]:
    async with session_factory() as session:
        yield session
        await session.rollback()
