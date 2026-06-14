from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


@dataclass
class FakeUoW:
    session: Any
    _autocommit: bool = False

    def __call__(self, *args: object, autocommit: bool = False, **kwargs: object) -> FakeUoW:
        self._autocommit = autocommit
        return self

    async def __aenter__(self) -> FakeUoW:
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def rollback(self) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None


@pytest.fixture
def fake_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def fake_uow(fake_session: AsyncMock) -> FakeUoW:
    return FakeUoW(session=fake_session)


def make_scalar_result(value: object | None) -> MagicMock:
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    result.scalars.return_value.all.return_value = value if isinstance(value, list) else []
    return result
