from __future__ import annotations

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ApplicationError


def unwrap_ok_or_http_exc[T](result: AppResult[T]) -> T:
    if isinstance(result, Err):
        raise ApplicationError(result.error)  # type: ignore[arg-type]
    if isinstance(result, Ok):
        return result.value
    raise TypeError(f"Unexpected result type: {type(result)!r}")
