from __future__ import annotations

import pytest

from migrations.seeds.task_catalog_seed import build_task_catalog
from src.shared.execution.checking.flow_error_hints import enrich_flow_pattern_errors
from src.shared.execution.checking.flow_source_alignment import (
    extract_text_requirements,
    normalize_flow_text,
    validate_flowchart_source_alignment,
)
from src.shared.execution.checking.flow_validation_service import FlowValidationService


def _node(node_id: str, block_type: str, text: str = "") -> dict:
    return {"id": node_id, "type": block_type, "text": text, "x": 0, "y": 0}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


def _validate(
    *,
    nodes: list[dict],
    edges: list[dict],
    flow_spec: dict,
    source_code: str | None = None,
    constructions: list[str] | None = None,
    flow: list[dict] | None = None,
) -> dict:
    service = FlowValidationService()
    return service.validate_with_details(
        flow=flow or [],
        flow_spec=flow_spec,
        task={
            "constructions": constructions or [],
            "source_code": source_code,
        },
        nodes=nodes,
        edges=edges,
    )


# ---------------------------------------------------------------------------
# Дыра: contains_any пропускает неверный range, если нет source_code
# ---------------------------------------------------------------------------


def test_regression__loose_text_checks_pass_wrong_range_without_source_code() -> None:
    """Документирует дыру: без source_code проверка текста слишком мягкая."""
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "for i in range(2)"),
        _node("3", "output", "print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]

    result = _validate(
        nodes=nodes,
        edges=edges,
        flow_spec={
            "required_sequence": ["start", "loop", "output", "end"],
            "required_text_checks": [
                {"type": "loop", "contains_any": ["for", "range"]},
                {"type": "output", "contains_any": ["print"]},
            ],
            "require_loop_back_edge": True,
        },
        source_code=None,
    )

    assert result["errors"] == []


def test_regression__source_code_closes_wrong_range_hole() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", "for i in range(2)"),
        _node("3", "output", "print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]

    result = _validate(
        nodes=nodes,
        edges=edges,
        flow_spec={
            "required_sequence": ["start", "loop", "output", "end"],
            "required_text_checks": [
                {"type": "loop", "contains_any": ["for", "range"]},
            ],
            "require_loop_back_edge": True,
        },
        source_code="for i in range(3):\n    print(i)",
    )

    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in result["errors"])
    assert result["debug"]["source_alignment_failures"]


# ---------------------------------------------------------------------------
# Source alignment: типичные ошибки студентов
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source_code", "nodes", "should_fail"),
    [
        (
            "while n > 0:\n    print(n)\n    n -= 1",
            [
                _node("1", "loop", "while n > 1"),
                _node("2", "output", "print(n)"),
                _node("3", "process", "n -= 1"),
            ],
            True,
        ),
        (
            "while n > 0:\n    print(n)\n    n -= 1",
            [
                _node("1", "loop", "while n > 0"),
                _node("2", "output", "print(n)"),
                _node("3", "process", "n -= 1"),
            ],
            False,
        ),
        (
            "if n > 0:\n    print('pos')\nelse:\n    print('nonpos')",
            [
                _node("1", "decision", "n >= 0"),
                _node("2", "output", "pos"),
                _node("3", "output", "nonpos"),
            ],
            True,
        ),
        (
            "if pwd == 'secret':\n    print('ok')\nelse:\n    print('denied')",
            [
                _node("1", "decision", "pwd == 'wrong'"),
                _node("2", "output", "ok"),
                _node("3", "output", "denied"),
            ],
            True,
        ),
        (
            "print(1)\nprint(2)",
            [
                _node("1", "output", "print(1)"),
                _node("2", "output", "print(2)"),
            ],
            False,
        ),
        (
            "print(1)\nprint(2)",
            [
                _node("1", "output", "print(1)"),
                _node("2", "output", "print(3)"),
            ],
            True,
        ),
        (
            "for i in range(1, 4):\n    print(i * 2)",
            [_node("1", "loop", "for i in range(1, 3)"), _node("2", "process", "i * 2"), _node("3", "output", "print")],
            True,
        ),
        (
            "name = input()\nprint(name)",
            [_node("1", "input", "read name"), _node("2", "output", "print(name)")],
            True,
        ),
        (
            "a = int(input())\nb = int(input())\nprint(a + b)",
            [
                _node("1", "input", "a = int(input())"),
                _node("2", "input", "b = int(input())"),
                _node("3", "output", "print(a - b)"),
            ],
            True,
        ),
    ],
)
def test_source_alignment__student_mistakes(
    source_code: str,
    nodes: list[dict],
    should_fail: bool,
) -> None:
    errors, _ = validate_flowchart_source_alignment(nodes, source_code)
    if should_fail:
        assert errors
    else:
        assert errors == []


def test_source_alignment__whitespace_is_ignored() -> None:
    nodes = [
        _node("1", "loop", "for i in range( 3 )"),
        _node("2", "output", "print(i)"),
    ]
    errors, _ = validate_flowchart_source_alignment(nodes, "for i in range(3):\n    print(i)")
    assert errors == []


def test_source_alignment__case_insensitive() -> None:
    nodes = [_node("1", "output", "PRINT('Hello')")]
    errors, _ = validate_flowchart_source_alignment(nodes, "print('hello')")
    assert errors == []


def test_extract_text_requirements__deduplicates_identical_rules() -> None:
    source = "for i in range(3):\n    print(i)\nfor j in range(3):\n    print(j)"
    requirements = extract_text_requirements(source)
    loop_rules = [item for item in requirements if item["block_types"] == ["loop"]]
    assert len(loop_rules) == 1


def test_normalize_flow_text__collapses_spaces() -> None:
    assert normalize_flow_text("  For   I  In  Range ( 3 )  ") == "foriinrange(3)"


# ---------------------------------------------------------------------------
# Структурные дыры
# ---------------------------------------------------------------------------


def test_regression__missing_start_block() -> None:
    result = _validate(
        nodes=[_node("1", "output", "print"), _node("2", "end")],
        edges=[_edge("1", "2")],
        flow_spec={},
    )
    assert any(item["type"] == "FLOW_START_MISSING" for item in result["errors"])


def test_regression__missing_end_block() -> None:
    result = _validate(
        nodes=[_node("1", "start"), _node("2", "output", "print")],
        edges=[_edge("1", "2")],
        flow_spec={},
    )
    assert any(item["type"] == "FLOW_END_MISSING" for item in result["errors"])


def test_regression__dead_end_process_block() -> None:
    result = _validate(
        nodes=[
            _node("1", "start"),
            _node("2", "process", "x = 1"),
            _node("3", "end"),
        ],
        edges=[_edge("1", "2"), _edge("1", "3")],
        flow_spec={},
    )
    assert any(item["type"] == "FLOW_DEAD_END" for item in result["errors"])


def test_regression__disconnected_end_is_not_end_unreachable_check() -> None:
    """Дыра: «Конец» вне графа даёт FLOW_DISCONNECTED, а не FLOW_END_UNREACHABLE."""
    result = _validate(
        nodes=[
            _node("1", "start"),
            _node("2", "output", "print"),
            _node("3", "end"),
        ],
        edges=[_edge("1", "2")],
        flow_spec={},
    )
    assert any(item["type"] == "FLOW_DISCONNECTED" for item in result["errors"])
    assert not any(item["type"] == "FLOW_END_UNREACHABLE" for item in result["errors"])


def test_regression__unsupported_block_type() -> None:
    result = _validate(
        nodes=[_node("1", "start"), _node("2", "subroutine"), _node("3", "end")],
        edges=[_edge("1", "2"), _edge("2", "3")],
        flow_spec={"allowed_blocks": ["start", "process", "end"]},
    )
    assert any(item["type"] == "FLOW_BLOCK_UNSUPPORTED" for item in result["errors"])


def test_regression__flow_list_order_used_for_sequence_check() -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "output", "print(1)"),
        _node("3", "output", "print(2)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]
    flow = [
        {"id": "1", "type": "start"},
        {"id": "2", "type": "output"},
        {"id": "3", "type": "output"},
        {"id": "4", "type": "end"},
    ]

    result = _validate(
        nodes=nodes,
        edges=edges,
        flow_spec={
            "required_sequence": ["start", "output", "output", "end"],
            "allow_extra_nodes": False,
        },
        flow=flow,
    )

    assert result["errors"] == []


def test_regression__swapped_output_text_passes_if_literals_present() -> None:
    """Дыра: порядок вывода не проверяется — достаточно наличия 1 и 2 в блоках."""
    nodes = [
        _node("1", "start"),
        _node("2", "output", "print(2)"),
        _node("3", "output", "print(1)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]

    result = _validate(
        nodes=nodes,
        edges=edges,
        flow_spec={
            "required_sequence": ["start", "output", "output", "end"],
            "allow_extra_nodes": False,
        },
        source_code="print(1)\nprint(2)",
    )

    assert result["errors"] == []


# ---------------------------------------------------------------------------
# Seed tasks: каждая должна ловить типичную ошибку в тексте
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("task_id", "nodes", "edges"),
    [
        (
            3,
            [
                _node("1", "start"),
                _node("2", "input", "n = int(input())"),
                _node("3", "decision", "n > 0 ?"),
                _node("4", "output", "pos"),
                _node("5", "output", "wrong"),
                _node("6", "end"),
            ],
            [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("3", "5"), _edge("4", "6"), _edge("5", "6")],
        ),
        (
            6,
            [_node("1", "start"), _node("2", "output", "print('hi')"), _node("3", "end")],
            [_edge("1", "2"), _edge("2", "3")],
        ),
        (
            42,
            [
                _node("1", "start"),
                _node("2", "decision", "answer == 'no'"),
                _node("3", "output", "yes"),
                _node("4", "output", "no"),
                _node("5", "end"),
            ],
            [_edge("1", "2"), _edge("2", "3"), _edge("2", "4"), _edge("3", "5"), _edge("4", "5")],
        ),
        (
            48,
            [
                _node("1", "start"),
                _node("2", "input", "pwd = input()"),
                _node("3", "decision", "pwd == 'public'"),
                _node("4", "output", "ok"),
                _node("5", "output", "denied"),
                _node("6", "end"),
            ],
            [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("3", "5"), _edge("4", "6"), _edge("5", "6")],
        ),
    ],
)
def test_seed_tasks__reject_wrong_block_text(task_id: int, nodes: list[dict], edges: list[dict]) -> None:
    catalog = {item["id"]: item for item in build_task_catalog()}
    payload = catalog[task_id]["payload"]

    result = _validate(
        nodes=nodes,
        edges=edges,
        flow_spec=payload["flow_spec"],
        source_code=payload.get("source_code"),
        constructions=payload.get("constructions") or [],
    )

    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in result["errors"])


def test_enrich_errors__includes_source_alignment_hint() -> None:
    errors = [{"type": "FLOW_SOURCE_MISMATCH", "text": "Неверный текст."}]
    debug = {
        "source_alignment_failures": [
            {"hint": "В блоке «Цикл» укажите условие range(3), как в программе."},
        ],
    }

    enriched = enrich_flow_pattern_errors(errors, debug)

    assert "range(3)" in enriched[0]["text"]
