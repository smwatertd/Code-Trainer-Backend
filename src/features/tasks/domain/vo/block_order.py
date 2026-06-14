from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ValidationFailure
from src.shared.student_messages import (
    BLOCK_INDEX_NEGATIVE,
    BLOCK_INDEX_OUT_OF_RANGE,
    BLOCK_ORDER_EMPTY,
    BLOCK_ORDER_LENGTH_MISMATCH,
)


@dataclass(frozen=True, slots=True)
class BlockOrder:
    indices: tuple[int, ...]

    @classmethod
    def create(
        cls,
        raw: list[int],
        *,
        blocks_count: int | None = None,
    ) -> AppResult[BlockOrder]:
        if not raw:
            return Err(ValidationFailure(BLOCK_ORDER_EMPTY))
        if any(index < 0 for index in raw):
            return Err(ValidationFailure(BLOCK_INDEX_NEGATIVE))
        if blocks_count is not None:
            if len(raw) != blocks_count:
                return Err(ValidationFailure(BLOCK_ORDER_LENGTH_MISMATCH))
            if max(raw) >= blocks_count:
                return Err(ValidationFailure(BLOCK_INDEX_OUT_OF_RANGE))
        return Ok(cls(tuple(raw)))

    def as_list(self) -> list[int]:
        return list(self.indices)
