from __future__ import annotations

from src.core.either import Ok
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.services.execution_service import ExecutionService
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.stores.memory_job_store import MemoryJobStore


def test_execution_service__deduplicates_inflight_job() -> None:
    store = MemoryJobStore()
    service = ExecutionService(store=store, auto_process=False, processor=GuestJobProcessor())

    first = service.submit(
        user_id="guest:abc",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=1,
    )
    second = service.submit(
        user_id="guest:abc",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=1,
    )

    assert isinstance(first, Ok)
    assert isinstance(second, Ok)
    assert first.value.deduplicated is False
    assert second.value.deduplicated is True
    assert first.value.job_id == second.value.job_id

    job = store.get_job(first.value.job_id)
    assert job is not None
    assert job.status is JobStatus.QUEUED
