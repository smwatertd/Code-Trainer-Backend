from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.containers import Container
from src.features.assignment_sets.models import AssignmentSetItemModel, AssignmentSetModel  # noqa: F401
from src.features.auth.models import AuthSessionModel, UserModel  # noqa: F401
from src.features.catalog.models import TaskModel  # noqa: F401
from src.features.groups.models import InvitationCodeModel, StudyGroupModel  # noqa: F401
from src.features.progress.models import (  # noqa: F401
    StudentCurriculumProgressModel,
    TaskCurriculumLinkModel,
    TaskProgressModel,
)
from src.features.submissions.models import SubmissionModel  # noqa: F401
from src.shared.database.base import Base

container = Container()
settings = container.config()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.db.dsn)
config.attributes["schema"] = settings.db.db_schema


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=settings.db.db_schema,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=settings.db.db_schema,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
