from __future__ import annotations

from enum import StrEnum


class JobStatus(StrEnum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"

    def is_terminal(self) -> bool:
        return self in {JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.TIMEOUT}
