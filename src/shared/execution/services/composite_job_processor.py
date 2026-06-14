from __future__ import annotations

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.interfaces.job_processor import JobProcessor
from src.shared.execution.services.guest_job_processor import GuestJobProcessor


class CompositeJobProcessor(JobProcessor):
    def __init__(self, guest_processor: GuestJobProcessor) -> None:
        self._guest_processor = guest_processor

    def process(self, job: ExecutionJob) -> dict[str, object]:
        if job.op in {"guest_full_check", "process_submission"}:
            return self._guest_processor.process(job)

        return {
            "success": False,
            "compiler_errors": [
                {"type": "UNSUPPORTED", "text": f"Unsupported execution op: {job.op}"},
            ],
        }
