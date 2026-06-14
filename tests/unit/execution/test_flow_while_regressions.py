from __future__ import annotations

from src.shared.execution.checking.flow_source_alignment import (
    block_text_matches_fragments,
    validate_flowchart_source_alignment,
)
from src.shared.execution.checking.flow_validation_service import FlowValidationService


def _node(node_id: str, node_type: str, text: str = "") -> dict:
    return {"id": node_id, "type": node_type, "text": text, "x": 0, "y": 0}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


SOURCE_WHILE = "n = 3\nwhile n > 0:\n    print(n)\n    n -= 1"


def test_block_text_matches_decrement_equivalents() -> None:
    assert block_text_matches_fragments("n -= 1", ["n-=1"])
    assert block_text_matches_fragments("n = n - 1", ["n-=1"])
    assert block_text_matches_fragments("n := n - 1", ["n-=1"])


def test_block_text_matches_multilingual_output() -> None:
    assert block_text_matches_fragments("WriteLn(n)", ["print"])
    assert block_text_matches_fragments("cout << n << endl;", ["print"])


def test_validate_while_flowchart_with_init_block_passes() -> None:
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
    service = FlowValidationService()
    result = service.validate_with_details(
        flow=[],
        flow_spec={
            "required_sequence": ["start", "loop", "output", "process", "end"],
            "required_text_checks": [
                {"type": "loop", "contains_any": ["while", ">"]},
                {"type": "output", "contains_any": ["print"]},
                {"type": "process", "contains_any": ["-=", "-"]},
            ],
            "allow_extra_nodes": False,
            "require_loop_back_edge": True,
        },
        task={"constructions": ["while_loop"], "source_code": SOURCE_WHILE},
        nodes=nodes,
        edges=edges,
    )

    assert result["errors"] == []


def test_validate_while_source_alignment_accepts_assign_decrement() -> None:
    nodes = [
        _node("1", "loop", "while n > 0"),
        _node("2", "output", "print(n)"),
        _node("3", "process", "n = n - 1"),
    ]
    errors, _ = validate_flowchart_source_alignment(nodes, SOURCE_WHILE)
    assert errors == []
