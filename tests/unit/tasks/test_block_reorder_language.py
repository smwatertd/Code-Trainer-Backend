from __future__ import annotations

from src.features.tasks.domain.block_reorder_language import (
    assemble_block_reorder_code,
    block_reorder_statements,
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


def test_assemble_block_reorder_code__wraps_cpp_program() -> None:
    code = assemble_block_reorder_code(
        ['cout << "b" << endl;', 'cout << "a" << endl;'],
        [0, 1],
        "cpp",
    )

    assert code.startswith("#include <iostream>")
    assert "int main()" in code
    assert code.endswith("}")
