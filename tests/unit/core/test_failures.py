from __future__ import annotations

import pytest

from src.core.either.failures import (
    ApplicationError,
    ConflictFailure,
    InfrastructureFailure,
    NotFoundFailure,
    UnknownFailure,
    ValidationFailure,
)


@pytest.mark.parametrize(
    ("failure_cls", "args", "code", "status_code"),
    [
        (ValidationFailure, ("Email is invalid",), "VALIDATION_ERROR", 422),
        (NotFoundFailure, ("Task", "42"), "NOT_FOUND", 404),
        (ConflictFailure, ("Already exists",), "CONFLICT", 409),
        (InfrastructureFailure, ("Queue unavailable",), "INFRASTRUCTURE_ERROR", 503),
        (UnknownFailure, (), "UNKNOWN_ERROR", 500),
    ],
)
def test_failure__exposes_code_and_status(
    failure_cls: type,
    args: tuple[str, ...],
    code: str,
    status_code: int,
) -> None:
    failure = failure_cls(*args)

    assert failure.code == code
    assert failure.status_code == status_code
    assert code in repr(failure)


def test_application_error__wraps_failure() -> None:
    failure = NotFoundFailure("Task", "7")
    error = ApplicationError(failure)

    assert error.failure is failure
