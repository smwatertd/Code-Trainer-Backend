from __future__ import annotations

from src.shared.execution.checking.flow_block_constructions import (
    format_sequence_labels,
    label_block_type,
    validate_constructions_from_blocks,
)


def test_label_block_type__russian_labels() -> None:
    assert label_block_type("loop") == "Цикл"
    assert label_block_type("decision") == "Условие"
    assert label_block_type("unknown") == "unknown"


def test_format_sequence_labels() -> None:
    assert format_sequence_labels(["start", "loop", "end"]) == "Начало → Цикл → Конец"


def test_validate_constructions__if_statement_requires_decision() -> None:
    errors, debug = validate_constructions_from_blocks(
        submitted_types=["start", "input", "output", "end"],
        constructions=["if_statement"],
    )

    assert len(errors) == 1
    assert errors[0]["type"] == "FLOW_CONSTRUCTION_MISSING"
    assert debug[0]["construction"] == "if_statement"


def test_validate_constructions__for_loop_requires_loop_block() -> None:
    errors, _ = validate_constructions_from_blocks(
        submitted_types=["start", "output", "end"],
        constructions=["for_loop"],
    )

    assert errors[0]["type"] == "FLOW_CONSTRUCTION_MISSING"


def test_validate_constructions__nested_loops_requires_two_loop_blocks() -> None:
    errors, debug = validate_constructions_from_blocks(
        submitted_types=["start", "loop", "output", "end"],
        constructions=["nested_loops"],
    )

    assert errors[0]["type"] == "FLOW_CONSTRUCTION_MISSING"
    assert debug[0]["required_count"] == "2"


def test_validate_constructions__io_requires_input_and_output() -> None:
    errors, debug = validate_constructions_from_blocks(
        submitted_types=["start", "input", "end"],
        constructions=["io"],
    )

    assert errors[0]["type"] == "FLOW_CONSTRUCTION_MISSING"
    assert "output" in debug[0]["missing_block_types"]


def test_validate_constructions__passes_when_requirements_met() -> None:
    errors, debug = validate_constructions_from_blocks(
        submitted_types=["start", "decision", "output", "output", "end"],
        constructions=["if_statement"],
    )

    assert errors == []
    assert debug == []


def test_validate_constructions__deduplicates_tags() -> None:
    errors, debug = validate_constructions_from_blocks(
        submitted_types=["start", "output", "end"],
        constructions=["for_loop", "for_loop"],
    )

    assert len(errors) == 1
    assert len(debug) == 1
