from __future__ import annotations

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ValidationFailure
from src.features.tasks.domain.vo.block_order import BlockOrder
from src.shared.student_messages import (
    ASSEMBLED_CODE_MISMATCH,
    ASSEMBLED_CODE_REQUIRED,
    BLOCK_ORDER_EMPTY,
    BLOCKS_WRONG_ORDER,
)


def matches_correct_order(submitted: list[int], correct: list[int]) -> bool:
    return list(submitted) == list(correct)


def _normalize_program_code(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _is_structural_program(lines: list[str]) -> bool:
    joined = " ".join(line.strip().lower() for line in lines if line.strip())
    return (
        "program " in joined
        or joined.startswith("begin")
        or "#include" in joined
        or "public class" in joined
        or "using system" in joined
    )


def validate_block_order_answer(
    *,
    submitted_order: list[int],
    correct_order: list[int],
    blocks_count: int,
) -> AppResult[BlockOrder]:
    order_result = BlockOrder.create(submitted_order, blocks_count=blocks_count)
    if order_result.is_err():
        return order_result

    if not matches_correct_order(submitted_order, correct_order):
        return Err(ValidationFailure(BLOCKS_WRONG_ORDER))

    return order_result


def validate_block_order_structure(
    *,
    submitted_order: list[int],
    correct_order: list[int],
    assembled_code: str | None,
    expected_code: str,
) -> AppResult[None]:
    if not submitted_order:
        return Err(ValidationFailure(BLOCK_ORDER_EMPTY))
    if not matches_correct_order(submitted_order, correct_order):
        return Err(ValidationFailure(BLOCKS_WRONG_ORDER))

    submitted = (assembled_code or "").strip()
    if not submitted:
        return Err(ValidationFailure(ASSEMBLED_CODE_REQUIRED))

    if _normalize_program_code(submitted) != _normalize_program_code(expected_code):
        return Err(ValidationFailure(ASSEMBLED_CODE_MISMATCH))

    return Ok(None)
