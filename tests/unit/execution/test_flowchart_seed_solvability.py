from __future__ import annotations

import pytest

from tests.fixtures.flowchart_sample_tasks import (
    FLOWCHART_SAMPLE_CATALOG,
    FLOWCHART_SAMPLE_IDS,
    flowchart_test_id,
)
from src.shared.execution.checking.flow_validation_service import FlowValidationService


def _node(node_id: str, block_type: str, text: str = "") -> dict:
    return {"id": node_id, "type": block_type, "text": text, "x": 0, "y": 0}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


def _flow(*steps: tuple[str, str, str]) -> list[dict]:
    return [{"id": node_id, "type": block_type, "text": text} for node_id, block_type, text in steps]


def _validate(task_id: int, nodes: list[dict], edges: list[dict], flow: list[dict]) -> list[dict]:
    task = FLOWCHART_SAMPLE_CATALOG[task_id]
    payload = task["payload"]
    service = FlowValidationService()
    result = service.validate_with_details(
        flow=flow,
        flow_spec=payload["flow_spec"],
        task={
            "constructions": payload.get("constructions") or [],
            "source_code": payload.get("source_code"),
        },
        nodes=nodes,
        edges=edges,
    )
    return result["errors"]


def test_flowchart_seed__task3_if_else() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "input", "n = int(input())"),
        _node("3", "decision", "n > 0 ?"),
        _node("4", "output", "pos"),
        _node("5", "output", "nonpos"),
        _node("6", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("3", "5"), _edge("4", "6"), _edge("5", "6")]
    flow = _flow(
        ("1", "start", ""),
        ("2", "input", "n = int(input())"),
        ("3", "decision", "n > 0 ?"),
        ("4", "output", "pos"),
        ("5", "output", "nonpos"),
        ("6", "end", ""),
    )
    assert _validate(flowchart_test_id(3), nodes, edges, flow) == []


def test_flowchart_seed__task40_for_loop_with_back_edge() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "for i in range(3)"),
        _node("3", "output", "print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]
    flow = _flow(
        ("1", "start", ""),
        ("2", "loop", "for i in range(3)"),
        ("3", "output", "print(i)"),
        ("4", "end", ""),
    )
    assert _validate(flowchart_test_id(40), nodes, edges, flow) == []


def test_flowchart_seed__task44_while_loop_with_back_edge() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "while n > 0"),
        _node("3", "output", "print(n)"),
        _node("4", "process", "n -= 1"),
        _node("5", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("4", "2"), _edge("2", "5")]
    flow = _flow(
        ("1", "start", ""),
        ("2", "loop", "while n > 0"),
        ("3", "output", "print(n)"),
        ("4", "process", "n -= 1"),
        ("5", "end", ""),
    )
    assert _validate(flowchart_test_id(44), nodes, edges, flow) == []


def test_flowchart_seed__task44_while_with_init_and_assign_decrement() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "process", "n = 3"),
        _node("3", "loop", "while n > 0"),
        _node("4", "output", "print(n)"),
        _node("5", "process", "n = n - 1"),
        _node("6", "end"),
    ]
    edges = [
        _edge("1", "2"),
        _edge("2", "3"),
        _edge("3", "4"),
        _edge("4", "5"),
        _edge("5", "3"),
        _edge("3", "6"),
    ]
    flow = _flow(
        ("1", "start", ""),
        ("2", "process", "n = 3"),
        ("3", "loop", "while n > 0"),
        ("4", "output", "print(n)"),
        ("5", "process", "n = n - 1"),
        ("6", "end", ""),
    )
    assert _validate(flowchart_test_id(44), nodes, edges, flow) == []


def test_flowchart_seed__task49_table_loop() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "for i in range(1, 4)"),
        _node("3", "process", "i * 2"),
        _node("4", "output", "print"),
        _node("5", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("4", "2"), _edge("2", "5")]
    flow = _flow(
        ("1", "start", ""),
        ("2", "loop", "for i in range(1, 4)"),
        ("3", "process", "i * 2"),
        ("4", "output", "print"),
        ("5", "end", ""),
    )
    assert _validate(flowchart_test_id(49), nodes, edges, flow) == []


def test_flowchart_seed__task40_rejects_wrong_range() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "for i in range(2)"),
        _node("3", "output", "print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]
    flow = _flow(
        ("1", "start", ""),
        ("2", "loop", "for i in range(2)"),
        ("3", "output", "print(i)"),
        ("4", "end", ""),
    )
    errors = _validate(flowchart_test_id(40), nodes, edges, flow)
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in errors)


def test_flowchart_seed__task40_rejects_loop_without_back_edge() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "for i in range(3)"),
        _node("3", "output", "print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]
    flow = _flow(
        ("1", "start", ""),
        ("2", "loop", "for i in range(3)"),
        ("3", "output", "print(i)"),
        ("4", "end", ""),
    )
    errors = _validate(flowchart_test_id(40), nodes, edges, flow)
    assert any(error["type"] == "FLOW_LOOP_BACK_EDGE" for error in errors)


def test_all_flowchart_sample_tasks_have_specs_and_tests() -> None:
    for task_id in FLOWCHART_SAMPLE_IDS:
        task = FLOWCHART_SAMPLE_CATALOG[task_id]
        assert task["task_type"] == "task_flowchart_to_code"
        assert task["payload"]["flow_spec"]["required_sequence"]
        assert task["payload"].get("test_cases"), f"task {task_id} missing test_cases"
