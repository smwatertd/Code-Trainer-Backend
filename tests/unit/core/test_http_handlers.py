from __future__ import annotations

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import ValidationFailure
from src.core.either.result import Ok as OkType
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc


def test_unwrap_ok_or_http_exc__returns_value_on_ok() -> None:
    value = unwrap_ok_or_http_exc(Ok(42))

    assert value == 42


def test_unwrap_ok_or_http_exc__raises_application_error_on_err() -> None:
    failure = ValidationFailure("Invalid input")

    with pytest.raises(Exception) as exc_info:
        unwrap_ok_or_http_exc(Err(failure))

    assert exc_info.value.failure is failure  # type: ignore[attr-defined]
    assert exc_info.value.failure.code == "VALIDATION_ERROR"  # type: ignore[attr-defined]


def test_unwrap_ok_or_http_exc__raises_type_error_on_unknown_result() -> None:
    class BrokenResult:
        pass

    with pytest.raises(TypeError, match="Unexpected result type"):
        unwrap_ok_or_http_exc(BrokenResult())  # type: ignore[arg-type]


def test_ok__is_ok_and_unwrap() -> None:
    result: OkType[int] = Ok(7)

    assert result.is_ok() is True
    assert result.is_err() is False
    assert result.unwrap() == 7


def test_err__is_err_and_unwrap_err() -> None:
    failure = ValidationFailure("bad")
    result = Err(failure)

    assert result.is_ok() is False
    assert result.is_err() is True
    assert result.unwrap_err() is failure
