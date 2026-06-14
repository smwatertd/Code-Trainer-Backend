from __future__ import annotations

import re

_LANGUAGES = ("python", "cpp", "pascal", "java", "csharp")
_PRINT_QUOTED = re.compile(r"""^print\((['"])(.+?)\1\)$""")
_PRINT_NUMBER = re.compile(r"^print\((\d+)\)$")


def localize_block(line: str, language: str) -> str:
    if language == "python":
        return line

    text = line.strip()
    quoted = _PRINT_QUOTED.match(text)
    if quoted:
        value = quoted.group(2)
        if language == "cpp":
            return f'cout << "{value}" << endl;'
        if language == "pascal":
            return f"WriteLn('{value}');"
        if language == "java":
            return f'System.out.println("{value}");'
        return f'Console.WriteLine("{value}");'

    numbered = _PRINT_NUMBER.match(text)
    if numbered:
        value = numbered.group(1)
        if language == "cpp":
            return f"cout << {value} << endl;"
        if language == "pascal":
            return f"WriteLn({value});"
        if language == "java":
            return f"System.out.println({value});"
        return f"Console.WriteLine({value});"

    return line


def blocks_by_language(python_blocks: list[str]) -> dict[str, list[str]]:
    return {language: [localize_block(line, language) for line in python_blocks] for language in _LANGUAGES}


def block_reorder_payload(
    *,
    blocks: list[str],
    correct_order: list[int],
    expected_code: str,
    output: str,
    topics: list[str],
) -> dict:
    return {
        "language": "python",
        "blocks": blocks,
        "blocks_by_language": blocks_by_language(blocks),
        "correct_order": correct_order,
        "expected_code": expected_code,
        "test_cases": [{"inputs": "", "output": output}],
        "topics": topics,
    }
