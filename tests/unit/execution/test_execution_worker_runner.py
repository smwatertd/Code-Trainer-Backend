from __future__ import annotations

from dataclasses import dataclass, field

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.services.execution_worker_runner import ExecutionWorkerRunner
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.stores.memory_job_store import MemoryJobStore


@dataclass
class _GuestLifecycleSpy:
    finished_ips: list[str] = field(default_factory=list)

    def on_job_finished(self, client_ip: str) -> None:
        self.finished_ips.append(client_ip)


def test_execution_worker_runner__processes_guest_block_reorder() -> None:
    store = MemoryJobStore()
    guest = _GuestLifecycleSpy()
    runner = ExecutionWorkerRunner(
        store=store,
        processor=GuestJobProcessor(),
        guest_lifecycle=guest,
    )
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print('b')\nprint('a')",
        op="guest_full_check",
        task_id=2,
        payload={
            "client_ip": "127.0.0.1",
            "task_snapshot": {
                "task_type": "task_build_from_blocks",
                "payload": {
                    "correct_order": [1, 0],
                    "expected_code": "print('b')\nprint('a')",
                },
            },
            "block_order": [1, 0],
        },
    )
    store.save_job(job)
    store.enqueue(job.job_id)

    runner.process_job(job)

    updated = store.get_job(job.job_id)
    assert updated is not None
    assert updated.status is JobStatus.SUCCESS
    assert guest.finished_ips == ["127.0.0.1"]


def test_execution_worker_runner__process_next_blocking_drains_queue() -> None:
    store = MemoryJobStore()
    runner = ExecutionWorkerRunner(store=store, processor=GuestJobProcessor())
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="x",
        op="guest_full_check",
        payload={"task_snapshot": {"task_type": "translation", "payload": {}}},
    )
    store.save_job(job)
    store.enqueue(job.job_id)

    processed = runner.process_next_blocking(timeout=0)

    assert processed is True
    assert store.get_job(job.job_id).status is JobStatus.SUCCESS  # type: ignore[union-attr]
