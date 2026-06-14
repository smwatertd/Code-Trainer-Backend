from __future__ import annotations

from unittest.mock import MagicMock

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.services.composite_job_processor import CompositeJobProcessor
from src.shared.execution.services.guest_job_processor import GuestJobProcessor


def test_composite_job_processor__routes_guest_check() -> None:
    processor = CompositeJobProcessor(guest_processor=GuestJobProcessor())
    job = ExecutionJob.create(
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

    output = processor.process(job)

    assert output["success"] is True


def test_composite_job_processor__routes_process_submission() -> None:
    processor = CompositeJobProcessor(guest_processor=GuestJobProcessor())
    job = ExecutionJob.create(
        user_id="42",
        language_id="python",
        code="print('b')\nprint('a')",
        op="process_submission",
        task_id=2,
        payload={
            "submission_id": 9,
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

    output = processor.process(job)

    assert output["success"] is True


def test_composite_job_processor__rejects_unknown_op() -> None:
    processor = CompositeJobProcessor(guest_processor=MagicMock())
    job = ExecutionJob.create(
        user_id="1",
        language_id="python",
        code="pass",
        op="compile_check",
    )

    output = processor.process(job)

    assert output["success"] is False
