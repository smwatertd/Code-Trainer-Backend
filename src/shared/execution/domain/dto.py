from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JobQueuedDTO:
    job_id: str
    status: str
    deduplicated: bool = False


@dataclass(frozen=True)
class JobStatusDTO:
    job_id: str
    status: str
    language_id: str | None = None
    op: str | None = None


@dataclass(frozen=True)
class JobResultDTO:
    job_id: str
    status: str
    success: bool | None = None
    output: dict[str, Any] | None = None
    errors: str | None = None
