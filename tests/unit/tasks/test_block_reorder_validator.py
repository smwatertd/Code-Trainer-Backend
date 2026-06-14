from __future__ import annotations

from src.core.either import Err, Ok
from src.features.tasks.domain.enums import TaskFamily, task_family_from_legacy_type
from src.features.tasks.domain.vo.block_order import BlockOrder
from src.features.tasks.domain.vo.task_id import TaskId
from src.features.tasks.services.block_reorder_validator import (
    matches_correct_order,
    validate_block_order_answer,
    validate_block_order_structure,
)


def test_task_family_from_legacy_type__maps_block_reorder() -> None:
    assert task_family_from_legacy_type("task_build_from_blocks") is TaskFamily.BLOCK_REORDER


def test_task_id__create__accepts_positive() -> None:
    result = TaskId.create(7)

    assert isinstance(result, Ok)
    assert result.value.value == 7


def test_block_order__create__rejects_out_of_range() -> None:
    result = BlockOrder.create([0, 2], blocks_count=2)

    assert isinstance(result, Err)


def test_validate_block_order_answer__accepts_correct_order() -> None:
    result = validate_block_order_answer(
        submitted_order=[1, 0],
        correct_order=[1, 0],
        blocks_count=2,
    )

    assert isinstance(result, Ok)
    assert result.value.as_list() == [1, 0]


def test_validate_block_order_answer__rejects_wrong_order() -> None:
    result = validate_block_order_answer(
        submitted_order=[0, 1],
        correct_order=[1, 0],
        blocks_count=2,
    )

    assert isinstance(result, Err)
    assert result.error.code == "VALIDATION_ERROR"


def test_validate_block_order_structure__requires_matching_code() -> None:
    result = validate_block_order_structure(
        submitted_order=[0, 1],
        correct_order=[0, 1],
        assembled_code="print(1)\nprint(2)",
        expected_code="print(1)\nprint(2)",
    )

    assert isinstance(result, Ok)


def test_matches_correct_order() -> None:
    assert matches_correct_order([0, 1], [0, 1]) is True
    assert matches_correct_order([1, 0], [0, 1]) is False
