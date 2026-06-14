from __future__ import annotations

import pytest

from src.core.either import Err, Ok
from src.features.tasks.domain.vo.task_id import TaskId


@pytest.mark.parametrize("raw", [0, -3])
def test_create__rejects_non_positive(raw: int) -> None:
    result = TaskId.create(raw)

    assert isinstance(result, Err)
    assert result.error.message == "Task id must be a positive integer"


def test_create__accepts_positive_integer() -> None:
    result = TaskId.create(101)

    assert isinstance(result, Ok)
    assert str(result.value) == "101"
