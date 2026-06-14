from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TaskSummaryDTO:
    id: int
    title: str
    description: str
    difficulty: str
    task_type: str
    topics: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    progress_status: str | None = None


@dataclass(frozen=True)
class TaskDetailDTO:
    id: int
    title: str
    description: str
    difficulty: str
    task_type: str
    payload: dict[str, Any]
