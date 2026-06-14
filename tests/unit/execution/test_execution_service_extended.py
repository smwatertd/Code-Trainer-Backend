from __future__ import annotations

from src.core.either import Err, Ok
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.services.execution_service import ExecutionService
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.stores.memory_job_store import MemoryJobStore


def _block_reorder_payload() -> dict:
    return {
        "task_snapshot": {
            "task_type": "task_build_from_blocks",
            "payload": {
                "correct_order": [1, 0],
                "expected_code": "print('b')\nprint('a')",
            },
        },
        "block_order": [1, 0],
    }


def test_execution_service__dedup_returns_same_job_id() -> None:
    store = MemoryJobStore()
    service = ExecutionService(store=store, auto_process=False, processor=GuestJobProcessor())
    kwargs = {
        "user_id": "guest:1.1.1.1",
        "language_id": "python",
        "code": "print('b')\nprint('a')",
        "op": "guest_full_check",
        "task_id": 2,
        "payload": _block_reorder_payload(),
    }

    first = service.submit(**kwargs)
    second = service.submit(**kwargs)

    assert isinstance(first, Ok)
    assert isinstance(second, Ok)
    assert first.value.job_id == second.value.job_id
    assert second.value.deduplicated is True


def test_execution_service__get_status_unknown_job() -> None:
    service = ExecutionService(store=MemoryJobStore(), auto_process=False)

    result = service.get_status("missing-job")

    assert isinstance(result, Err)


def test_execution_service__get_result_before_terminal_state() -> None:
    store = MemoryJobStore()
    service = ExecutionService(store=store, auto_process=False, processor=GuestJobProcessor())
    submit = service.submit(
        user_id="guest:9.9.9.9",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=2,
        payload={"guest": True},
    )
    assert isinstance(submit, Ok)

    status = service.get_status(submit.value.job_id)
    assert isinstance(status, Ok)
    assert status.value.status == JobStatus.QUEUED.value

    result = service.get_result(submit.value.job_id)
    assert isinstance(result, Ok)
    assert result.value.status == JobStatus.QUEUED.value


def test_execution_service__submit_without_auto_process_keeps_queued() -> None:
    service = ExecutionService(store=MemoryJobStore(), auto_process=False)
    submit = service.submit(
        user_id="guest:local",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=2,
    )
    assert isinstance(submit, Ok)

    status = service.get_status(submit.value.job_id)
    assert isinstance(status, Ok)
    assert status.value.status == JobStatus.QUEUED.value
