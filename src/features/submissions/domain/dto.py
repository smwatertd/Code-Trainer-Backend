from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SubmissionDetailDTO:
    id: int
    user_id: int | None
    task_id: int
    language: str
    status: str
    success: bool | None
    created_at: str | None
    updated_at: str | None
    compiler_errors: list[dict[str, Any]]
    linter_errors: list[dict[str, Any]]
    pattern_errors: list[dict[str, Any]]
    test_results: list[dict[str, Any]]
    duration_ms: int | None = None
    code: str = ""
    block_order: list[int] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    flow: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class SubmissionHistoryItemDTO:
    id: int
    task_id: int
    language: str
    status: str
    success: bool | None
    created_at: str | None
    duration_ms: int | None


@dataclass(frozen=True)
class SubmissionAbandonedDTO:
    released: bool
    status: str


@dataclass(frozen=True)
class SubmissionQueuedDTO:
    id: int
    status: str
