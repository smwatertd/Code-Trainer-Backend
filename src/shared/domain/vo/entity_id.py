from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ValidationFailure


@dataclass(frozen=True, slots=True)
class PositiveIntId:
    """Шаблон typed id: парсинг path/query int → доменный id в use case."""

    value: int

    @classmethod
    def create(cls, raw: int) -> AppResult[PositiveIntId]:
        if raw <= 0:
            return Err(ValidationFailure("Id must be a positive integer"))
        return Ok(cls(raw))

    def __str__(self) -> str:
        return str(self.value)
