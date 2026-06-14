from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Database(ABC):
    @property
    @abstractmethod
    def engine(self) -> Any: ...

    @property
    @abstractmethod
    def session_factory(self) -> Any: ...
