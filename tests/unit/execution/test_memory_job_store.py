from __future__ import annotations

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.stores.memory_job_store import MemoryJobStore


def test_memory_job_store__save_and_get() -> None:
    store = MemoryJobStore()
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=1,
    )

    store.save_job(job)
    loaded = store.get_job(job.job_id)

    assert loaded is not None
    assert loaded.job_id == job.job_id


def test_memory_job_store__update_status_and_result() -> None:
    store = MemoryJobStore()
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
    )
    store.save_job(job)

    updated = store.update_status(job.job_id, JobStatus.SUCCESS)
    store.save_result(job.job_id, {"output": {"success": True}})

    assert updated is not None
    assert updated.status is JobStatus.SUCCESS
    assert store.get_result(job.job_id) == {"output": {"success": True}}


def test_memory_job_store__queue_fifo() -> None:
    store = MemoryJobStore()
    store.enqueue("a")
    store.enqueue("b")

    assert store.dequeue() == "a"
    assert store.dequeue() == "b"
    assert store.dequeue() is None
