from __future__ import annotations

from pathlib import Path

import pytest

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.code_runner_factory import create_code_runner
from src.shared.execution.checking.flow_validation_service import FlowValidationService
from src.shared.execution.pipeline.flowchart_pipeline import FlowchartPipeline
from src.shared.execution.pipeline.translation_pipeline import TranslationPipeline

_LANGUAGES_DIR = Path(__file__).resolve().parents[3] / "languages"


def _node(node_id: str, node_type: str, *, x: float = 0, y: float = 0, text: str = "") -> dict:
    return {"id": node_id, "type": node_type, "text": text, "x": x, "y": y}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


@pytest.fixture
def flowchart_pipeline() -> FlowchartPipeline:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    code_runner = create_code_runner(registry, prefer_docker=False)
    translation = TranslationPipeline(code_runner)
    return FlowchartPipeline(
        translation_pipeline=translation,
        flow_validator=FlowValidationService(),
        code_runner=code_runner,
    )


def test_flowchart_pipeline__code_to_flowchart_success(flowchart_pipeline: FlowchartPipeline) -> None:
    nodes = [
        _node("1", "start", y=0),
        _node("2", "input", y=100, text="readln(n)"),
        _node("3", "decision", y=200, text="n > 0 ?"),
        _node("4", "output", y=300, text="writeln('pos')"),
        _node("5", "output", y=400, text="writeln('nonpos')"),
        _node("6", "end", y=500),
    ]
    edges = [
        _edge("1", "2"),
        _edge("2", "3"),
        _edge("3", "4"),
        _edge("3", "5"),
        _edge("4", "6"),
        _edge("5", "6"),
    ]
    task_payload = {
        "flowchart_mode": "code_to_flowchart",
        "flow_spec": {
            "required_sequence": ["start", "input", "decision", "output", "output", "end"],
            "required_text_checks": [
                {"type": "input", "contains_any": ["readln", "n"]},
                {"type": "decision", "contains_any": ["> 0"]},
                {"type": "output", "contains_any": ["pos"]},
                {"type": "output", "contains_any": ["nonpos"]},
            ],
            "allow_extra_nodes": False,
        },
        "constructions": ["if_statement"],
    }

    result = flowchart_pipeline.run(
        language_id="python",
        code=".",
        task_type="task_flowchart_to_code",
        task_payload=task_payload,
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is True
    assert result["pattern_errors"] == []


def test_flowchart_pipeline__code_to_flowchart_missing_decision(flowchart_pipeline: FlowchartPipeline) -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "input", text="readln(n)"),
        _node("3", "output", text="writeln('pos')"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]

    result = flowchart_pipeline.run(
        language_id="python",
        code=".",
        task_type="task_flowchart_to_code",
        task_payload={
            "flowchart_mode": "code_to_flowchart",
            "flow_spec": {},
            "constructions": ["if_statement"],
        },
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is False
    assert any(item["type"] == "FLOW_CONSTRUCTION_MISSING" for item in result["pattern_errors"])


def test_flowchart_pipeline__code_to_flowchart_success_without_semantic_tests(
    flowchart_pipeline: FlowchartPipeline,
) -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "output", text="print('hello')"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]
    task_payload = {
        "flowchart_mode": "code_to_flowchart",
        "source_code": "print('hello')",
        "flow_spec": {
            "required_sequence": ["start", "output", "end"],
            "required_text_checks": [{"type": "output", "contains_any": ["hello"]}],
            "allow_extra_nodes": False,
        },
        "test_cases": [{"inputs": "", "output": "hello"}],
    }

    result = flowchart_pipeline.run(
        language_id="python",
        code="print('hello')",
        task_type="task_flowchart_to_code",
        task_payload=task_payload,
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is True
    assert result["semantic_checked"] is False
    assert result["test_results"] == []


def test_flowchart_pipeline__structural_failure_skips_semantic(flowchart_pipeline: FlowchartPipeline) -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "end"),
    ]
    edges = [_edge("1", "2")]

    result = flowchart_pipeline.run(
        language_id="python",
        code="print('hello')",
        task_type="task_flowchart_to_code",
        task_payload={
            "flowchart_mode": "code_to_flowchart",
            "flow_spec": {"required_sequence": ["start", "output", "end"]},
            "test_cases": [{"inputs": "", "output": "hello"}],
        },
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is False
    assert result["semantic_checked"] is False
    assert result["test_results"] == []


def test_flowchart_pipeline__rejects_wrong_range_in_loop_text(
    flowchart_pipeline: FlowchartPipeline,
) -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "loop", text="for i in range(2)"),
        _node("3", "output", text="print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]

    result = flowchart_pipeline.run(
        language_id="python",
        code="for i in range(3):\n    print(i)",
        task_type="task_flowchart_to_code",
        task_payload={
            "flowchart_mode": "code_to_flowchart",
            "source_code": "for i in range(3):\n    print(i)",
            "flow_spec": {
                "required_sequence": ["start", "loop", "output", "end"],
                "required_text_checks": [
                    {"type": "loop", "contains_any": ["for", "range"]},
                ],
                "require_loop_back_edge": True,
            },
            "test_cases": [{"inputs": "", "output": "0\n1\n2\n"}],
        },
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is False
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in result["pattern_errors"])
    assert result["semantic_checked"] is False


def test_flowchart_pipeline__wrong_range_would_pass_if_only_loose_checks(
    flowchart_pipeline: FlowchartPipeline,
) -> None:
    """Документирует: без source_code pipeline принимал бы неверный range."""
    nodes = [
        _node("1", "start"),
        _node("2", "loop", text="for i in range(2)"),
        _node("3", "output", text="print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]

    result = flowchart_pipeline.run(
        language_id="python",
        code=".",
        task_type="task_flowchart_to_code",
        task_payload={
            "flowchart_mode": "code_to_flowchart",
            "flow_spec": {
                "required_sequence": ["start", "loop", "output", "end"],
                "required_text_checks": [
                    {"type": "loop", "contains_any": ["for", "range"]},
                ],
                "require_loop_back_edge": True,
            },
        },
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is True


def test_flowchart_pipeline__source_mismatch_omits_internal_debug(
    flowchart_pipeline: FlowchartPipeline,
) -> None:
    nodes = [
        _node("1", "start"),
        _node("2", "output", text="print('bye')"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]

    result = flowchart_pipeline.run(
        language_id="python",
        code="print('hello')",
        task_type="task_flowchart_to_code",
        task_payload={
            "flowchart_mode": "code_to_flowchart",
            "source_code": "print('hello')",
            "flow_spec": {
                "required_sequence": ["start", "output", "end"],
                "allow_extra_nodes": False,
            },
        },
        job_payload={"nodes": nodes, "edges": edges},
    )

    assert result["success"] is False
    assert "flow_debug" not in result
    assert any(item["type"] == "FLOW_SOURCE_MISMATCH" for item in result["pattern_errors"])
