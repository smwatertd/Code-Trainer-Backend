from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ValidationFailure


@dataclass(frozen=True, slots=True)
class TaskId:
    value: int

    @classmethod
    def create(cls, raw: int) -> AppResult[TaskId]:
        if raw <= 0:
            return Err(ValidationFailure("Task id must be a positive integer"))
        return Ok(cls(raw))

    def __str__(self) -> str:
        return str(self.value)
