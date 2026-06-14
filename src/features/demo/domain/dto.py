from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DemoCheckQueuedDTO:
    job_id: str
    status: str


@dataclass(frozen=True)
class DemoCheckResultDTO:
    job_id: str
    status: str
    success: bool | None = None
    compiler_errors: list[dict[str, Any]] | None = None
    linter_errors: list[dict[str, Any]] | None = None
    pattern_errors: list[dict[str, Any]] | None = None
    test_results: list[dict[str, Any]] | None = None
    errors: str | None = None
