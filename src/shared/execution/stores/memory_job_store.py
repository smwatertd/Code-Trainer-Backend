from __future__ import annotations

from collections import deque
from typing import Any

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.interfaces.job_store import JobStore


class MemoryJobStore(JobStore):
    def __init__(self) -> None:
        self._jobs: dict[str, ExecutionJob] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._queue: deque[str] = deque()
        self._dedup: dict[str, str] = {}

    def get_dedup_job_id(self, dedup_key: str) -> str | None:
        return self._dedup.get(dedup_key)

    def bind_dedup(self, dedup_key: str, job_id: str) -> None:
        self._dedup[dedup_key] = job_id

    def save_job(self, job: ExecutionJob) -> None:
        self._jobs[job.job_id] = job

    def get_job(self, job_id: str) -> ExecutionJob | None:
        return self._jobs.get(job_id)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error: str | None = None,
    ) -> ExecutionJob | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.status = status
        job.updated_at = ExecutionJob.now_iso()
        if error is not None:
            job.error = error
        self._jobs[job_id] = job
        return job

    def save_result(self, job_id: str, result: dict[str, Any]) -> None:
        self._results[job_id] = result

    def get_result(self, job_id: str) -> dict[str, Any] | None:
        return self._results.get(job_id)

    def enqueue(self, job_id: str) -> None:
        self._queue.append(job_id)

    def dequeue(self) -> str | None:
        if not self._queue:
            return None
        return self._queue.popleft()

    def dequeue_blocking(self, timeout: int) -> ExecutionJob | None:
        _ = timeout
        job_id = self.dequeue()
        if not job_id:
            return None
        return self.get_job(job_id)

    def clear(self) -> None:
        self._jobs.clear()
        self._results.clear()
        self._queue.clear()
        self._dedup.clear()

    def queue_depth(self) -> int:
        return len(self._queue)
