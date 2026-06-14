from __future__ import annotations

import pytest

from src.shared.analysis.concept_ast_detector import concept_present, detect_concepts
from src.shared.analysis.educational_validator import EducationalValidator
from src.shared.analysis.tree_sitter_gateway import parse_code
from src.shared.execution.checking.pattern_checker import PatternChecker


def test_detect_concepts__finds_for_loop_in_python() -> None:
    code = "for i in range(3):\n    print(i)\n"
    tree = parse_code(code, "python")

    result = detect_concepts(tree, "python", code)

    assert "loop" in result.detected


def test_concept_present__condition_in_if() -> None:
    code = "if x > 0:\n    print(x)\n"
    tree = parse_code(code, "python")

    assert concept_present(tree, "python", "condition", code) is True


def test_educational_validator__missing_loop_for_for_loop_tag() -> None:
    validator = EducationalValidator()
    result = validator.validate("print(1)\n", "python", ["for_loop"])

    assert result.is_valid is False
    assert "loop" in result.missing


def test_educational_validator__passes_when_loop_present() -> None:
    validator = EducationalValidator()
    result = validator.validate("for i in range(3):\n    print(i)\n", "python", ["for_loop"])

    assert result.is_valid is True


def test_pattern_checker__returns_russian_missing_label() -> None:
    checker = PatternChecker()
    errors = checker.check("print(1)\n", "python", ["for_loop"])

    assert len(errors) == 1
    assert "конструкция" in errors[0].lower()


@pytest.mark.parametrize(
    "code,constructions,expected_valid",
    [
        ("for i in range(3):\n    print(i)\n", ["for_loop"], True),
        ("while i < 3:\n    i += 1\n", ["while_loop"], True),
        ("print(1)\n", ["for_loop"], False),
    ],
)
def test_educational_validator__construction_tags(code: str, constructions: list[str], expected_valid: bool) -> None:
    validator = EducationalValidator()
    result = validator.validate(code, "python", constructions)

    assert result.is_valid is expected_valid
