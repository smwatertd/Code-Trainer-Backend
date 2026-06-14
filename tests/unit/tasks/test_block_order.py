from __future__ import annotations

import pytest

from src.core.either import Err, Ok
from src.features.tasks.domain.vo.block_order import BlockOrder


@pytest.mark.parametrize("raw", [[], [-1, 0]])
def test_create__rejects_invalid_indices(raw: list[int]) -> None:
    result = BlockOrder.create(raw)

    assert isinstance(result, Err)
    assert result.error.code == "VALIDATION_ERROR"


def test_create__rejects_duplicate_indices_when_out_of_range() -> None:
    result = BlockOrder.create([0, 2], blocks_count=2)

    assert isinstance(result, Err)


def test_create__accepts_valid_permutation() -> None:
    result = BlockOrder.create([2, 0, 1], blocks_count=3)

    assert isinstance(result, Ok)
    assert result.value.as_list() == [2, 0, 1]


def test_as_list__returns_mutable_copy() -> None:
    order = BlockOrder.create([1, 0], blocks_count=2)
    assert isinstance(order, Ok)

    copied = order.value.as_list()
    copied.append(99)

    assert order.value.as_list() == [1, 0]
