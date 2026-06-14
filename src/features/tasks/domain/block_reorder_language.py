from __future__ import annotations

import re
from typing import Any

BLOCK_REORDER_LANGUAGES = ("python", "cpp", "pascal", "java", "csharp")

_PRINT_QUOTED = re.compile(r"""^print\((['"])(.+?)\1\)$""")
_PRINT_NUMBER = re.compile(r"^print\((\d+)\)$")

BLOCK_REORDER_TEMPLATES: dict[str, dict[str, str]] = {
    "python": {"header": "", "footer": "", "joiner": "\n", "line_prefix": ""},
    "cpp": {
        "header": "#include <iostream>\nusing namespace std;\n\nint main() {\n",
        "footer": "\n    return 0;\n}",
        "joiner": "\n",
        "line_prefix": "    ",
    },
    "pascal": {
        "header": "program Solution;\nbegin\n",
        "footer": "\nend.",
        "joiner": "\n",
        "line_prefix": "  ",
    },
    "java": {
        "header": "public class Solution {\n  public static void main(String[] args) {\n",
        "footer": "\n  }\n}\n",
        "joiner": "\n",
        "line_prefix": "    ",
    },
    "csharp": {
        "header": "using System;\n\nclass Solution {\n  static void Main() {\n",
        "footer": "\n  }\n}\n",
        "joiner": "\n",
        "line_prefix": "    ",
    },
}


def _template(language_id: str) -> dict[str, str]:
    return BLOCK_REORDER_TEMPLATES.get(language_id, BLOCK_REORDER_TEMPLATES["python"])


def assemble_block_reorder_code(blocks: list[str], order: list[int], language_id: str) -> str:
    template = _template(language_id)
    line_prefix = template.get("line_prefix", "")
    lines = [blocks[index] for index in order if 0 <= index < len(blocks)]
    body_lines = [
        f"{line_prefix}{line}" if line_prefix and not line.startswith(line_prefix) else line for line in lines
    ]
    body = template["joiner"].join(body_lines)
    return f'{template["header"]}{body}{template["footer"]}'


def localize_block_statement(line: str, language_id: str) -> str:
    if language_id == "python":
        return line

    text = line.strip()
    quoted = _PRINT_QUOTED.match(text)
    if quoted:
        value = quoted.group(2)
        if language_id == "cpp":
            return f'cout << "{value}" << endl;'
        if language_id == "pascal":
            return f"WriteLn('{value}');"
        if language_id == "java":
            return f'System.out.println("{value}");'
        if language_id == "csharp":
            return f'Console.WriteLine("{value}");'

    numbered = _PRINT_NUMBER.match(text)
    if numbered:
        value = numbered.group(1)
        if language_id == "cpp":
            return f"cout << {value} << endl;"
        if language_id == "pascal":
            return f"WriteLn({value});"
        if language_id == "java":
            return f"System.out.println({value});"
        if language_id == "csharp":
            return f"Console.WriteLine({value});"

    return line


def synthesize_blocks_by_language(statements: list[str]) -> dict[str, list[str]]:
    return {
        language_id: [localize_block_statement(line, language_id) for line in statements]
        for language_id in BLOCK_REORDER_LANGUAGES
    }


def _base_block_statements(payload: dict[str, Any]) -> list[str]:
    variants = payload.get("blocks_by_language")
    if isinstance(variants, dict):
        default_language = str(payload.get("language") or "python")
        for key in (default_language, "python", *variants.keys()):
            raw = variants.get(key)
            if isinstance(raw, list) and raw:
                return [str(item) for item in raw]

    blocks = payload.get("blocks") or []
    return [str(item) for item in blocks]


def block_reorder_statements(payload: dict[str, Any], language_id: str) -> list[str]:
    variants = payload.get("blocks_by_language")
    if isinstance(variants, dict):
        raw = variants.get(language_id)
        if isinstance(raw, list) and raw:
            return [str(item) for item in raw]

    base = _base_block_statements(payload)
    return [localize_block_statement(line, language_id) for line in base]


def resolve_expected_block_reorder_code(payload: dict[str, Any], language_id: str) -> str:
    by_language = payload.get("expected_code_by_language")
    if isinstance(by_language, dict) and language_id in by_language:
        return str(by_language[language_id])

    default_language = str(payload.get("language") or "python")
    explicit_expected = str(payload.get("expected_code") or "")
    if default_language == language_id and explicit_expected:
        return explicit_expected

    correct_order = list(payload.get("correct_order") or [])
    statements = block_reorder_statements(payload, language_id)
    if correct_order and statements:
        return assemble_block_reorder_code(statements, correct_order, language_id)

    return explicit_expected
