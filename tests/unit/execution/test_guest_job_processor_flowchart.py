from __future__ import annotations

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.services.guest_job_processor import GuestJobProcessor


def _for_loop_job(*, loop_text: str, with_back_edge: bool = True) -> ExecutionJob:
    nodes = [
        {"id": "1", "type": "start"},
        {"id": "2", "type": "loop", "text": loop_text},
        {"id": "3", "type": "output", "text": "print(i)"},
        {"id": "4", "type": "end"},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
    ]
    if with_back_edge:
        edges.append({"source": "3", "target": "2"})
    edges.append({"source": "2", "target": "4"})

    return ExecutionJob.create(
        user_id="guest:test",
        language_id="python",
        code="for i in range(3):\n    print(i)",
        op="guest_full_check",
        task_id=40,
        payload={
            "task_snapshot": {
                "task_type": "task_flowchart_to_code",
                "payload": {
                    "flowchart_mode": "code_to_flowchart",
                    "source_code": "for i in range(3):\n    print(i)",
                    "flow_spec": {
                        "required_sequence": ["start", "loop", "output", "end"],
                        "require_loop_back_edge": True,
                    },
                },
            },
            "nodes": nodes,
            "edges": edges,
        },
    )


def test_guest_job_processor__flowchart_wrong_range_fails() -> None:
    processor = GuestJobProcessor()
    output = processor.process(_for_loop_job(loop_text="for i in range(2)"))

    assert output["success"] is False
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in output["pattern_errors"])
    assert "flow_debug" not in output


def test_guest_job_processor__flowchart_correct_range_passes() -> None:
    processor = GuestJobProcessor()
    output = processor.process(_for_loop_job(loop_text="for i in range(3)"))

    assert output["success"] is True
    assert output["pattern_errors"] == []
    assert "flow_debug" not in output


def test_guest_job_processor__flowchart_missing_back_edge_fails() -> None:
    processor = GuestJobProcessor()
    output = processor.process(_for_loop_job(loop_text="for i in range(3)", with_back_edge=False))

    assert output["success"] is False
    assert any(item["type"] == "FLOW_LOOP_BACK_EDGE" for item in output["pattern_errors"])


def test_guest_job_processor__flowchart_empty_graph_fails() -> None:
    processor = GuestJobProcessor()
    job = ExecutionJob.create(
        user_id="guest:test",
        language_id="python",
        code="print('hello')",
        op="guest_full_check",
        task_id=6,
        payload={
            "task_snapshot": {
                "task_type": "task_flowchart_to_code",
                "payload": {
                    "flowchart_mode": "code_to_flowchart",
                    "source_code": "print('hello')",
                    "flow_spec": {"required_sequence": ["start", "output", "end"]},
                },
            },
            "nodes": [],
            "edges": [],
        },
    )

    output = processor.process(job)

    assert output["success"] is False
    assert any(item["type"] == "FLOW_EMPTY" for item in output["pattern_errors"])
