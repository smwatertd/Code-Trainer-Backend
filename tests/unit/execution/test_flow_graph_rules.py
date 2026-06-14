from __future__ import annotations

from src.shared.execution.checking.flow_graph_rules import (
    has_back_edge_to,
    sequence_types_from_flow,
    validate_loop_constructions,
)


def _node(node_id: str, block_type: str) -> dict:
    return {"id": node_id, "type": block_type}


def test_sequence_types_from_flow__preserves_student_order() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop"),
        _node("3", "output"),
        _node("4", "end"),
    ]
    flow = [
        {"id": "1", "type": "start"},
        {"id": "2", "type": "loop"},
        {"id": "3", "type": "output"},
        {"id": "4", "type": "end"},
    ]

    assert sequence_types_from_flow(flow, nodes) == ["start", "loop", "output", "end"]


def test_sequence_types_from_flow__falls_back_to_node_types() -> None:
    nodes = [_node("1", "start"), _node("2", "output")]
    flow = [{"id": "1"}, {"id": "2"}]

    assert sequence_types_from_flow(flow, nodes) == ["start", "output"]


def test_sequence_types_from_flow__empty() -> None:
    assert sequence_types_from_flow([], []) == []


def test_has_back_edge_to__detects_return_from_body() -> None:
    adjacency = {
        "loop": ["body"],
        "body": ["loop"],
    }

    assert has_back_edge_to("loop", adjacency, {"loop", "body"}) is True


def test_has_back_edge_to__false_when_body_exits_only() -> None:
    adjacency = {
        "loop": ["body"],
        "body": ["end"],
        "end": [],
    }

    assert has_back_edge_to("loop", adjacency, {"loop", "body", "end"}) is False


def test_has_back_edge_to__ignores_sibling_branch() -> None:
    adjacency = {
        "loop": ["body", "end"],
        "body": ["end"],
        "end": [],
    }

    assert has_back_edge_to("loop", adjacency, {"loop", "body", "end"}) is False


def test_validate_loop_constructions__requires_back_edge_when_flag_set() -> None:
    nodes = [_node("1", "loop"), _node("2", "process")]
    adjacency = {"1": ["2"], "2": []}

    errors = validate_loop_constructions(
        nodes=nodes,
        adjacency=adjacency,
        visited_ids={"1", "2"},
        constructions=[],
        require_loop_back_edge=True,
    )

    assert any(item["type"] == "FLOW_LOOP_BACK_EDGE" for item in errors)


def test_validate_loop_constructions__passes_with_back_edge() -> None:
    nodes = [_node("1", "loop"), _node("2", "process")]
    adjacency = {"1": ["2"], "2": ["1"]}

    errors = validate_loop_constructions(
        nodes=nodes,
        adjacency=adjacency,
        visited_ids={"1", "2"},
        constructions=[],
        require_loop_back_edge=True,
    )

    assert errors == []


def test_validate_loop_constructions__for_loop_tag_without_loop_block() -> None:
    nodes = [_node("1", "start"), _node("2", "output")]
    adjacency = {"1": ["2"], "2": []}

    errors = validate_loop_constructions(
        nodes=nodes,
        adjacency=adjacency,
        visited_ids={"1", "2"},
        constructions=["for_loop"],
        require_loop_back_edge=False,
    )

    assert any(item["type"] == "FLOW_CONSTRUCTION_MISSING" for item in errors)


def test_validate_loop_constructions__decision_anchor_for_while_tag() -> None:
    nodes = [_node("1", "decision"), _node("2", "output")]
    adjacency = {"1": ["2"], "2": ["1"]}

    errors = validate_loop_constructions(
        nodes=nodes,
        adjacency=adjacency,
        visited_ids={"1", "2"},
        constructions=["while_loop"],
        require_loop_back_edge=False,
    )

    assert errors == []
