from __future__ import annotations

import pytest

from src.shared.execution.checking.flow_source_alignment import (
    extract_text_requirements,
    validate_flowchart_source_alignment,
)


def _node(node_id: str, block_type: str, text: str) -> dict:
    return {"id": node_id, "type": block_type, "text": text}


def test_extract_text_requirements__for_range() -> None:
    requirements = extract_text_requirements("for i in range(3):\n    print(i)")
    loop_req = next(item for item in requirements if item["block_types"] == ["loop"])
    assert loop_req["contains_all"] == ["range(3)"]


def test_extract_text_requirements__for_range_with_start_stop() -> None:
    requirements = extract_text_requirements("for i in range(1, 4):\n    print(i)")
    loop_req = next(item for item in requirements if item["block_types"] == ["loop"])
    assert loop_req["contains_all"] == ["range(1,4)"]


def test_extract_text_requirements__while_condition() -> None:
    requirements = extract_text_requirements("while n > 0:\n    print(n)")
    loop_req = next(item for item in requirements if item["block_types"] == ["loop"])
    assert loop_req["contains_all"] == ["n>0"]


def test_extract_text_requirements__if_condition() -> None:
    requirements = extract_text_requirements("if a < b:\n    print(a)")
    decision_req = next(item for item in requirements if item["block_types"] == ["decision"])
    assert decision_req["contains_all"] == ["a<b"]


def test_extract_text_requirements__quoted_print() -> None:
    requirements = extract_text_requirements("print('done')")
    output_req = next(item for item in requirements if item["block_types"] == ["output"])
    assert output_req["contains_all"] == ["done"]


def test_extract_text_requirements__expression_print_splits_process_and_output() -> None:
    requirements = extract_text_requirements("print(i * 2)")
    assert any(item["block_types"] == ["process"] and item["contains_all"] == ["i*2"] for item in requirements)
    assert any(item["block_types"] == ["output"] and item["contains_all"] == ["print"] for item in requirements)


def test_extract_text_requirements__int_input() -> None:
    requirements = extract_text_requirements("a = int(input())")
    assert any(item["block_types"] == ["input"] and "int" in item["contains_all"] for item in requirements)


def test_extract_text_requirements__string_input() -> None:
    requirements = extract_text_requirements("name = input()")
    assert any(item["block_types"] == ["input"] and item["contains_all"] == ["input"] for item in requirements)


def test_extract_text_requirements__aug_assign() -> None:
    requirements = extract_text_requirements("n -= 1")
    process_req = next(item for item in requirements if item["block_types"] == ["process"])
    assert process_req["contains_all"] == ["n-=1"]


def test_extract_text_requirements__function_definition() -> None:
    requirements = extract_text_requirements("def greet():\n    return 'hi'")
    assert any(item["block_types"] == ["process"] and item["contains_all"] == ["greet"] for item in requirements)


def test_extract_text_requirements__empty_source() -> None:
    assert extract_text_requirements("") == []
    assert extract_text_requirements("   \n  ") == []


def test_validate_flowchart_source_alignment__rejects_wrong_range() -> None:
    nodes = [
        _node("1", "loop", "for i in range(2)"),
        _node("2", "output", "print(i)"),
    ]
    errors, failures = validate_flowchart_source_alignment(
        nodes,
        "for i in range(3):\n    print(i)",
    )
    assert errors
    assert errors[0]["type"] == "FLOW_SOURCE_MISMATCH"
    assert failures


def test_validate_flowchart_source_alignment__accepts_correct_range() -> None:
    nodes = [
        _node("1", "loop", "for i in range(3)"),
        _node("2", "output", "print(i)"),
    ]
    errors, _ = validate_flowchart_source_alignment(
        nodes,
        "for i in range(3):\n    print(i)",
    )
    assert errors == []


def test_validate_flowchart_source_alignment__each_print_needs_own_output_block() -> None:
    nodes = [
        _node("1", "output", "print(1)"),
        _node("2", "output", "print(1)"),
    ]
    errors, _ = validate_flowchart_source_alignment(nodes, "print(1)\nprint(2)")
    assert errors


def test_validate_flowchart_source_alignment__rejects_missing_process_for_expression() -> None:
    nodes = [_node("1", "output", "print")]
    errors, _ = validate_flowchart_source_alignment(nodes, "print(i * 2)")
    assert errors


def test_validate_flowchart_source_alignment__accepts_readln_and_writeln_notation() -> None:
    nodes = [
        _node("1", "input", "readln(n)"),
        _node("2", "decision", "n > 0 ?"),
        _node("3", "output", "writeln('pos')"),
        _node("4", "output", "writeln('nonpos')"),
    ]
    source = "n = int(input())\n" "if n > 0:\n" "    print('pos')\n" "else:\n" "    print('nonpos')"
    errors, _ = validate_flowchart_source_alignment(nodes, source)
    assert errors == []


def test_validate_flowchart_source_alignment__accepts_assign_decrement_form() -> None:
    nodes = [
        _node("1", "loop", "while n > 0"),
        _node("2", "output", "print(n)"),
        _node("3", "process", "n = n - 1"),
    ]
    errors, _ = validate_flowchart_source_alignment(
        nodes,
        "while n > 0:\n    print(n)\n    n -= 1",
    )
    assert errors == []


def test_validate_flowchart_source_alignment__accepts_pascal_decrement_in_block() -> None:
    nodes = [
        _node("1", "loop", "while n > 0"),
        _node("2", "output", "WriteLn(n)"),
        _node("3", "process", "n := n - 1"),
    ]
    errors, _ = validate_flowchart_source_alignment(
        nodes,
        "while n > 0:\n    print(n)\n    n -= 1",
    )
    assert errors == []


@pytest.mark.parametrize(
    ("loop_text", "should_pass"),
    [
        ("for i in range(3)", True),
        ("FOR I IN RANGE(3)", True),
        ("for i in range(3):", True),
        ("for i in range(2)", False),
        ("for i in range(4)", False),
        ("while i < 3", False),
    ],
)
def test_validate_flowchart_source_alignment__range_variants(loop_text: str, should_pass: bool) -> None:
    nodes = [_node("1", "loop", loop_text), _node("2", "output", "print(i)")]
    errors, _ = validate_flowchart_source_alignment(nodes, "for i in range(3):\n    print(i)")
    assert (errors == []) is should_pass
