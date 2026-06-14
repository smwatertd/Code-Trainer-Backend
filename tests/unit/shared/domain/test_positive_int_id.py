from __future__ import annotations

import pytest

from src.core.either import Err, Ok
from src.shared.domain.vo import PositiveIntId


def test_positive_int_id__create__accepts_positive() -> None:
    result = PositiveIntId.create(42)

    assert isinstance(result, Ok)
    assert result.value.value == 42


@pytest.mark.parametrize("raw", [0, -1])
def test_positive_int_id__create__rejects_non_positive(raw: int) -> None:
    result = PositiveIntId.create(raw)

    assert isinstance(result, Err)
    assert result.error.code == "VALIDATION_ERROR"
