from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData()


def utc_now() -> datetime:
    return datetime.now(UTC)


def configure_search_path(engine: AsyncEngine, schema: str) -> None:
    if not schema or schema == "public":
        return

    @event.listens_for(engine.sync_engine, "connect")
    def _set_search_path(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute(f'SET search_path TO "{schema}"')
        cursor.close()
