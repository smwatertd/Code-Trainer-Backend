from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus


class JobStore(ABC):
    @abstractmethod
    def save_job(self, job: ExecutionJob) -> None: ...

    @abstractmethod
    def get_job(self, job_id: str) -> ExecutionJob | None: ...

    @abstractmethod
    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error: str | None = None,
    ) -> ExecutionJob | None: ...

    @abstractmethod
    def save_result(self, job_id: str, result: dict[str, Any]) -> None: ...

    @abstractmethod
    def get_result(self, job_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def enqueue(self, job_id: str) -> None: ...

    @abstractmethod
    def dequeue(self) -> str | None: ...

    def get_dedup_job_id(self, dedup_key: str) -> str | None:
        return None

    def bind_dedup(self, dedup_key: str, job_id: str) -> None:
        return None

    def dequeue_blocking(self, timeout: int) -> ExecutionJob | None:
        _ = timeout
        job_id = self.dequeue()
        if not job_id:
            return None
        return self.get_job(job_id)

    def decrement_queue_depth(self) -> None:
        return None

    def queue_depth(self) -> int:
        return 0
