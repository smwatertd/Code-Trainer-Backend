from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GetSubmissionCommand:
    submission_id: int
    user_id: int


@dataclass(frozen=True)
class GetLatestPendingSubmissionCommand:
    user_id: int
    task_id: int


@dataclass(frozen=True)
class SubmitSubmissionCommand:
    user_id: int
    task_id: int
    language: str
    code: str
    block_order: list[int] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    flow: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class AbandonSubmissionCommand:
    submission_id: int
    user_id: int


@dataclass(frozen=True)
class ListSubmissionHistoryCommand:
    user_id: int
    task_id: int
    limit: int = 20
