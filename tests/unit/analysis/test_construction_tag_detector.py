from __future__ import annotations

from migrations.seeds.tc42_course_catalog_generated import build_tc42_course_catalog
from src.shared.analysis.construction_tag_detector import (
    detect_construction_tags,
    missing_construction_tag_labels,
)
from src.shared.execution.checking.pattern_checker import PatternChecker


_AGE_PASCAL_OK = "\n".join(
    [
        "var age: integer;",
        "begin",
        "  readln(age);",
        "  writeln(age);",
        "end.",
    ]
)

_AGE_PASCAL_MISSING_READ = "\n".join(
    [
        "var age: integer;",
        "begin",
        "  age := 18;",
        "  writeln(age);",
        "end.",
    ]
)


def test_detect_construction_tags__pascal_begin_end_counts_as_program_entry() -> None:
    detected = detect_construction_tags(
        _AGE_PASCAL_OK,
        "pascal",
        ["program_entry", "typed_declaration", "stdin_read", "stdout_write"],
    )

    assert detected == {"program_entry", "typed_declaration", "stdin_read", "stdout_write"}


def test_missing_construction_tag_labels__reports_missing_stdin_read() -> None:
    missing = missing_construction_tag_labels(
        _AGE_PASCAL_MISSING_READ,
        "pascal",
        ["program_entry", "typed_declaration", "stdin_read", "stdout_write"],
    )

    assert missing == ["Отсутствует конструкция: Ввод с клавиатуры"]


def test_detect_construction_tags__pascal_mod_counts_as_arithmetic_ops() -> None:
    code = "\n".join(
        [
            "var x,last: integer;",
            "begin",
            "  readln(x);",
            "  last:=x mod 10;",
            "  writeln(last);",
            "end.",
        ]
    )
    detected = detect_construction_tags(code, "pascal", ["arithmetic_ops"])

    assert "arithmetic_ops" in detected


def test_pattern_checker__basics_constructions_for_age_task() -> None:
    checker = PatternChecker()
    missing = checker.check(
        _AGE_PASCAL_MISSING_READ,
        "pascal",
        ["program_entry", "typed_declaration", "stdin_read", "stdout_write"],
    )

    assert missing == ["Отсутствует конструкция: Ввод с клавиатуры"]


def test_pattern_checker__task8_last_digit_solution_passes_basics() -> None:
    checker = PatternChecker()
    code = "var x,last: integer;\nbegin\n  readln(x);\n  last:=x mod 10;\n  writeln(last);\nend."
    missing = checker.check(
        code,
        "pascal",
        ["program_entry", "typed_declaration", "assignment", "arithmetic_ops", "stdout_write"],
    )

    assert missing == []


def test_detect_construction_tags__pascal_readln_counts_as_assignment() -> None:
    code = "var a,b,c: integer;\nbegin\nreadln(a,b,c);\nwriteln(a);\nend."
    detected = detect_construction_tags(code, "pascal", ["assignment", "stdin_read"])

    assert "assignment" in detected
    assert "stdin_read" in detected


def test_detect_construction_tags__python_counted_loop() -> None:
    code = "n = int(input())\nfor i in range(n):\n    print(i)"
    detected = detect_construction_tags(code, "python", ["counted_loop"])

    assert "counted_loop" in detected


def test_seed_linear_search_task__uses_io_constructions() -> None:
    task = next(row for row in build_tc42_course_catalog() if row["id"] == 2)
    constructions = task["payload"]["constructions"]

    assert "stdin_read" in constructions
    assert "counted_loop" in constructions
