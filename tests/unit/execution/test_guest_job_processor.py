from __future__ import annotations

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.services.guest_job_processor import GuestJobProcessor


def _block_reorder_job(*, code: str, block_order: list[int]) -> ExecutionJob:
    return ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code=code,
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
            "block_order": block_order,
        },
    )


def test_guest_job_processor__block_reorder_success() -> None:
    processor = GuestJobProcessor()
    output = processor.process(_block_reorder_job(code="print('b')\nprint('a')", block_order=[1, 0]))

    assert output["success"] is True


def test_guest_job_processor__block_reorder_wrong_order() -> None:
    processor = GuestJobProcessor()
    output = processor.process(_block_reorder_job(code="print('a')\nprint('b')", block_order=[0, 1]))

    assert output["success"] is False


def test_guest_job_processor__translation_invalid_syntax_fails() -> None:
    processor = GuestJobProcessor()
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print('Hello'\n",
        op="guest_full_check",
        payload={"task_snapshot": {"task_type": "translation", "payload": {}}},
    )

    output = processor.process(job)

    assert output["success"] is False
    assert output["compiler_errors"]


def test_guest_job_processor__flowchart_structural_check() -> None:
    processor = GuestJobProcessor()
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code=".",
        op="guest_full_check",
        task_id=3,
        payload={
            "task_snapshot": {
                "task_type": "task_flowchart_to_code",
                "payload": {
                    "flowchart_mode": "code_to_flowchart",
                    "flow_spec": {"required_sequence": ["start", "input", "decision", "output", "output", "end"]},
                    "constructions": ["if_statement"],
                },
            },
            "nodes": [
                {"id": "1", "type": "start"},
                {"id": "2", "type": "input", "text": "readln(n)"},
                {"id": "3", "type": "decision", "text": "n > 0 ?"},
                {"id": "4", "type": "output", "text": "writeln('pos')"},
                {"id": "5", "type": "output", "text": "writeln('nonpos')"},
                {"id": "6", "type": "end"},
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "4"},
                {"source": "3", "target": "5"},
                {"source": "4", "target": "6"},
                {"source": "5", "target": "6"},
            ],
        },
    )

    output = processor.process(job)

    assert output["success"] is True
