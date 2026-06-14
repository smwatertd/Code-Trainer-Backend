from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Self


class UnitOfWork(ABC):
    def __call__(self, *args: Any, autocommit: bool = False, **kwargs: Any) -> Self:
        self._autocommit = autocommit
        return self

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        elif self._autocommit:
            await self.commit()
        await self.shutdown()

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...

    @property
    @abstractmethod
    def session(self) -> Any: ...
