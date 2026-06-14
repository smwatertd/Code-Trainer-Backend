from __future__ import annotations

import pytest

from src.shared.execution.checking.flow_validation_service import FlowValidationService
from tests.fixtures.flowchart_sample_tasks import (
    FLOWCHART_SAMPLE_CATALOG,
    FLOWCHART_SAMPLE_IDS,
    flowchart_test_id,
)


def _node(node_id: str, block_type: str, text: str = "") -> dict:
    return {"id": node_id, "type": block_type, "text": text, "x": 0, "y": 0}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


def _validate(task_id: int, nodes: list[dict], edges: list[dict]) -> list[dict]:
    task = FLOWCHART_SAMPLE_CATALOG[task_id]
    payload = task["payload"]
    service = FlowValidationService()
    result = service.validate_with_details(
        flow=[],
        flow_spec=payload["flow_spec"],
        task={
            "constructions": payload.get("constructions") or [],
            "source_code": payload.get("source_code"),
        },
        nodes=nodes,
        edges=edges,
    )
    return result["errors"]


@pytest.mark.parametrize("task_id", FLOWCHART_SAMPLE_IDS)
def test_seed_flowchart__empty_graph_fails(task_id: int) -> None:
    errors = _validate(task_id, [], [])
    assert any(item["type"] == "FLOW_EMPTY" for item in errors)


@pytest.mark.parametrize(
    "task_id",
    [
        flowchart_test_id(3),
        flowchart_test_id(6),
        flowchart_test_id(39),
        flowchart_test_id(40),
        flowchart_test_id(42),
        flowchart_test_id(48),
    ],
)
def test_seed_flowchart__start_only_fails(task_id: int) -> None:
    errors = _validate(task_id, [_node("1", "start")], [])
    assert errors


def test_seed_flowchart__task6_wrong_output_text_fails() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "output", "print('bye')"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]
    errors = _validate(flowchart_test_id(6), nodes, edges)
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in errors)


def test_seed_flowchart__task41_requires_two_distinct_outputs() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "output", "print(1)"),
        _node("3", "output", "print(1)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]
    errors = _validate(flowchart_test_id(41), nodes, edges)
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in errors)


def test_seed_flowchart__task43_wrong_sum_expression_fails() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "input", "a = int(input())"),
        _node("3", "input", "b = int(input())"),
        _node("4", "process", "a - b"),
        _node("5", "output", "print(a + b)"),
        _node("6", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("4", "5"), _edge("5", "6")]
    errors = _validate(flowchart_test_id(43), nodes, edges)
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in errors)


def test_seed_flowchart__task44_wrong_while_condition_fails() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "while n > 1"),
        _node("3", "output", "print(n)"),
        _node("4", "process", "n -= 1"),
        _node("5", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("4", "2"), _edge("2", "5")]
    errors = _validate(flowchart_test_id(44), nodes, edges)
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in errors)


def test_seed_flowchart__task6_minimal_valid_passes() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "output", "print('hello')"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]
    errors = _validate(flowchart_test_id(6), nodes, edges)
    assert errors == []
