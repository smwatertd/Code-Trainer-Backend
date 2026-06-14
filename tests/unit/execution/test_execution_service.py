from __future__ import annotations

from src.core.either import Ok
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.services.execution_service import ExecutionService
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.stores.memory_job_store import MemoryJobStore


def test_execution_service__submit_auto_processes_block_reorder() -> None:
    store = MemoryJobStore()
    processor = GuestJobProcessor()
    service = ExecutionService(store=store, auto_process=True, processor=processor)

    result = service.submit(
        user_id="guest:abc",
        language_id="python",
        code="print('b')\nprint('a')",
        op="guest_full_check",
        task_id=2,
        payload={
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

    assert isinstance(result, Ok)
    job_id = result.value.job_id
    status = service.get_status(job_id)
    assert isinstance(status, Ok)
    assert status.value.status == JobStatus.SUCCESS.value

    job_result = service.get_result(job_id)
    assert isinstance(job_result, Ok)
    assert job_result.value.success is True
