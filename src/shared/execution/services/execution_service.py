from __future__ import annotations

from typing import Any

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import NotFoundFailure
from src.shared.execution.domain.dto import JobQueuedDTO, JobResultDTO, JobStatusDTO
from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.execution_op import JobOp
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.interfaces.job_processor import JobProcessor
from src.shared.execution.interfaces.job_store import JobStore
from src.shared.execution.services.execution_worker_runner import ExecutionWorkerRunner
from src.shared.execution.services.job_builder import build_dedup_key


class ExecutionService:
    def __init__(
        self,
        store: JobStore,
        *,
        auto_process: bool = False,
        processor: JobProcessor | None = None,
    ) -> None:
        self._store = store
        self._auto_process = auto_process
        self._processor = processor

    def submit(
        self,
        *,
        user_id: str,
        language_id: str,
        code: str,
        op: JobOp,
        task_id: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> AppResult[JobQueuedDTO]:
        dedup_key = build_dedup_key(
            user_id=user_id,
            task_id=task_id,
            code=code,
            op=op,
            language_id=language_id,
            payload=payload,
        )
        existing_id = self._store.get_dedup_job_id(dedup_key)
        if existing_id:
            existing = self._store.get_job(existing_id)
            if existing and existing.status in {
                JobStatus.QUEUED,
                JobStatus.RUNNING,
                JobStatus.PENDING,
            }:
                return Ok(
                    JobQueuedDTO(
                        job_id=existing.job_id,
                        status=existing.status.value,
                        deduplicated=True,
                    )
                )

        job = ExecutionJob.create(
            user_id=user_id,
            language_id=language_id,
            code=code,
            op=op,
            task_id=task_id,
            payload=payload,
        )
        job.dedup_key = dedup_key
        self._store.save_job(job)
        job.status = JobStatus.QUEUED
        job.updated_at = ExecutionJob.now_iso()
        self._store.save_job(job)
        self._store.enqueue(job.job_id)
        self._store.bind_dedup(dedup_key, job.job_id)

        queued_status = job.status.value
        if self._auto_process:
            self.process_next()

        return Ok(JobQueuedDTO(job_id=job.job_id, status=queued_status, deduplicated=False))

    def get_status(self, job_id: str) -> AppResult[JobStatusDTO]:
        job = self._store.get_job(job_id)
        if not job:
            return Err(NotFoundFailure("Job", job_id))
        return Ok(
            JobStatusDTO(
                job_id=job.job_id,
                status=job.status.value,
                language_id=job.language_id,
                op=job.op,
            )
        )

    def get_result(self, job_id: str) -> AppResult[JobResultDTO]:
        job = self._store.get_job(job_id)
        if not job:
            return Err(NotFoundFailure("Job", job_id))

        if not job.status.is_terminal():
            return Ok(
                JobResultDTO(
                    job_id=job_id,
                    status=job.status.value,
                )
            )

        stored = self._store.get_result(job_id) or {}
        return Ok(
            JobResultDTO(
                job_id=job_id,
                status=job.status.value,
                success=bool((stored.get("output") or {}).get("success")) if job.status == JobStatus.SUCCESS else False,
                output=stored.get("output"),
                errors=stored.get("error") or job.error,
            )
        )

    def get_job(self, job_id: str) -> ExecutionJob | None:
        return self._store.get_job(job_id)

    def queue_depth(self) -> int:
        return self._store.queue_depth()

    def process_next(self) -> bool:
        if not self._processor:
            return False
        job_id = self._store.dequeue()
        if not job_id:
            return False
        job = self._store.get_job(job_id)
        if not job:
            return False
        runner = ExecutionWorkerRunner(self._store, self._processor)
        runner.process_job(job)
        return True
