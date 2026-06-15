from __future__ import annotations

from src.features.tasks.domain.block_reorder_language import (
    assemble_block_reorder_code,
    block_reorder_statements,
    resolve_block_reorder_correct_order,
    resolve_expected_block_reorder_code,
)


def test_localize_block_statement__converts_python_print_to_cpp() -> None:
    from src.features.tasks.domain.block_reorder_language import localize_block_statement

    assert localize_block_statement("print('a')", "cpp") == 'cout << "a" << endl;'
    assert localize_block_statement("print(1)", "java") == "System.out.println(1);"


def test_synthesize_blocks_by_language__builds_all_supported_languages() -> None:
    from src.features.tasks.domain.block_reorder_language import synthesize_blocks_by_language

    variants = synthesize_blocks_by_language(["print('a')", "print('b')"])

    assert variants["python"] == ["print('a')", "print('b')"]
    assert variants["cpp"][0] == 'cout << "a" << endl;'


def test_block_reorder_statements__localizes_when_variant_missing() -> None:
    payload = {
        "language": "python",
        "blocks": ["print('a')", "print('b')"],
        "blocks_by_language": {
            "python": ["print('a')", "print('b')"],
        },
    }

    assert block_reorder_statements(payload, "cpp") == [
        'cout << "a" << endl;',
        'cout << "b" << endl;',
    ]
    payload = {
        "language": "python",
        "blocks": ["print('a')", "print('b')"],
        "blocks_by_language": {
            "python": ["print('a')", "print('b')"],
            "cpp": ['cout << "a" << endl;', 'cout << "b" << endl;'],
        },
    }

    assert block_reorder_statements(payload, "cpp") == [
        'cout << "a" << endl;',
        'cout << "b" << endl;',
    ]


def test_resolve_expected_block_reorder_code__assembles_for_language() -> None:
    payload = {
        "language": "python",
        "blocks_by_language": {
            "python": ["print('a')", "print('b')"],
            "cpp": ['cout << "a" << endl;', 'cout << "b" << endl;'],
        },
        "correct_order": [1, 0],
        "expected_code": "print('b')\nprint('a')",
    }

    assert resolve_expected_block_reorder_code(payload, "python") == "print('b')\nprint('a')"

    cpp_expected = resolve_expected_block_reorder_code(payload, "cpp")
    assert 'cout << "b" << endl;' in cpp_expected
    assert 'cout << "a" << endl;' in cpp_expected
    assert cpp_expected.index('cout << "b"') < cpp_expected.index('cout << "a"')


def test_resolve_expected_block_reorder_code__assembles_structural_pascal_from_blocks() -> None:
    payload = {
        "language": "pascal",
        "blocks": ["program Main;", "begin", "writeln('Hello');", "end."],
        "blocks_by_language": {
            "pascal": ["program Main;", "begin", "writeln('Hello');", "end."],
        },
        "correct_order": [0, 1, 2, 3],
        "expected_code": "program Main;\nbegin\n  writeln('Hello');\nend.",
    }

    expected = resolve_expected_block_reorder_code(payload, "pascal")
    assert expected == "program Main;\nbegin\nwriteln('Hello');\nend."
    assert expected != payload["expected_code"]


def test_block_reorder_statements__uses_code_examples_when_blocks_mismatch_language() -> None:
    payload = {
        "language": "pascal",
        "blocks": ["program Main;", "begin", "writeln('Hello');", "end."],
        "blocks_by_language": {
            "pascal": ["program Main;", "begin", "writeln('Hello');", "end."],
        },
        "code_examples": {"python": "print('Hello')", "pascal": "program Main;\nbegin\n  writeln('Hello');\nend."},
    }

    assert block_reorder_statements(payload, "python") == ["print('Hello')"]


def test_resolve_block_reorder_correct_order__adapts_to_language_block_count() -> None:
    payload = {
        "language": "pascal",
        "correct_order": [0, 1, 2, 3],
        "code_examples": {"python": "print('Hello')"},
        "blocks_by_language": {"pascal": ["program Main;", "begin", "writeln('Hello');", "end."]},
    }

    python_statements = block_reorder_statements(payload, "python")
    assert resolve_block_reorder_correct_order(payload, "python", python_statements) == [0]


def test_assemble_block_reorder_code__wraps_cpp_program() -> None:
    code = assemble_block_reorder_code(
        ['cout << "b" << endl;', 'cout << "a" << endl;'],
        [0, 1],
        "cpp",
    )

    assert code.startswith("#include <iostream>")
    assert "int main()" in code
    assert code.endswith("}")


def test_assemble_block_reorder_code__keeps_structural_pascal_program() -> None:
    blocks = ["program Main;", "begin", "writeln('Hello');", "end."]
    code = assemble_block_reorder_code(blocks, [0, 1, 2, 3], "pascal")

    assert code.startswith("program Main;")
    assert "program Solution" not in code
    assert code.endswith("end.")


def test_resolve_expected_block_reorder_code__uses_submitted_order_when_provided() -> None:
    payload = {
        "language": "python",
        "blocks_by_language": {"python": ["print('a')", "print('b')"]},
        "correct_order": [0, 1],
        "expected_code": "print('a')\nprint('b')",
    }

    assert resolve_expected_block_reorder_code(payload, "python", order=[1, 0]) == "print('b')\nprint('a')"


def test_assemble_block_reorder_code__area_task_without_begin_body_indent() -> None:
    blocks = [
        "program Main;",
        "var w,h,area: integer;",
        "begin",
        "readln(w,h);",
        "area:=w*h;",
        "writeln(area);",
        "end.",
    ]
    order = list(range(len(blocks)))
    code = assemble_block_reorder_code(blocks, order, "pascal")

    assert "  readln" not in code
    assert code == (
        "program Main;\n"
        "var w,h,area: integer;\n"
        "begin\n"
        "readln(w,h);\n"
        "area:=w*h;\n"
        "writeln(area);\n"
        "end."
    )


def test_resolve_expected_block_reorder_code__falls_back_to_expected_code_by_language() -> None:
    payload = {
        "language": "python",
        "expected_code_by_language": {"python": "print('fallback')"},
    }

    assert resolve_expected_block_reorder_code(payload, "python") == "print('fallback')"
