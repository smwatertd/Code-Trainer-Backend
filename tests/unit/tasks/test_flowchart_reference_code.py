from __future__ import annotations

import pytest

from src.features.tasks.domain.flowchart_reference_code import (
    FLOWCHART_LANGUAGES,
    localize_flowchart_source,
    resolve_flowchart_reference_code,
    synthesize_flowchart_source_by_language,
)


def test_localize_flowchart_source__for_loop_cpp() -> None:
    source = "for i in range(3):\n    print(i)"
    result = localize_flowchart_source(source, "cpp")
    assert "for (int i = 0; i < 3; i++)" in result
    assert "cout << i << endl;" in result


def test_localize_flowchart_source__if_else_java() -> None:
    source = "n = int(input())\nif n > 0:\n    print('pos')\nelse:\n    print('nonpos')"
    result = localize_flowchart_source(source, "java")
    assert "if (n > 0)" in result
    assert "Scanner scanner" in result


def test_localize_flowchart_source__while_pascal() -> None:
    source = "n = 3\nwhile n > 0:\n    print(n)\n    n -= 1"
    result = localize_flowchart_source(source, "pascal")
    assert "while n > 0" in result
    assert "WriteLn" in result


def test_localize_flowchart_source__python_returns_unchanged() -> None:
    source = "print('hello')"
    assert localize_flowchart_source(source, "python") == source


@pytest.mark.parametrize("language_id", [lang for lang in FLOWCHART_LANGUAGES if lang != "python"])
def test_synthesize_flowchart_source_by_language__covers_all(language_id: str) -> None:
    variants = synthesize_flowchart_source_by_language("print('x')")
    assert language_id in variants
    assert variants[language_id].strip()


def test_resolve_flowchart_reference_code__uses_payload_variants() -> None:
    payload = {
        "source_code": "print('hello')",
        "source_code_by_language": {"python": "print('hello')", "cpp": 'cout << "hello" << endl;'},
    }
    assert resolve_flowchart_reference_code(payload, "cpp") == 'cout << "hello" << endl;'


def test_resolve_flowchart_reference_code__localizes_from_python_base() -> None:
    payload = {"source_code": "for i in range(2):\n    print(i)"}
    cpp = resolve_flowchart_reference_code(payload, "cpp")
    assert "for (int i = 0; i < 2; i++)" in cpp


def test_resolve_flowchart_reference_code__empty_payload() -> None:
    assert resolve_flowchart_reference_code({}, "python") == ""
