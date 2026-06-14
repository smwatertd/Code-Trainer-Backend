from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.interfaces.job_processor import JobProcessor
from src.shared.execution.interfaces.job_store import JobStore


class GuestJobLifecycle(Protocol):
    def on_job_finished(self, client_ip: str) -> None: ...


@dataclass
class ExecutionWorkerRunner:
    store: JobStore
    processor: JobProcessor
    guest_lifecycle: GuestJobLifecycle | None = None

    def process_job(self, job: ExecutionJob) -> None:
        self.store.update_status(job.job_id, JobStatus.RUNNING)
        try:
            output = self.processor.process(job)
            self.store.update_status(job.job_id, JobStatus.SUCCESS)
            self.store.save_result(
                job.job_id,
                {"status": JobStatus.SUCCESS.value, "output": output, "error": None},
            )
        except Exception as exc:
            self.store.update_status(job.job_id, JobStatus.FAILED, error=str(exc))
            self.store.save_result(
                job.job_id,
                {"status": JobStatus.FAILED.value, "output": None, "error": str(exc)},
            )
        finally:
            self.store.decrement_queue_depth()
            if job.op == "guest_full_check" and self.guest_lifecycle is not None:
                client_ip = str((job.payload or {}).get("client_ip") or "")
                if client_ip:
                    self.guest_lifecycle.on_job_finished(client_ip)

    def process_next_blocking(self, timeout: int) -> bool:
        job = self.store.dequeue_blocking(timeout)
        if not job:
            return False
        self.process_job(job)
        return True
