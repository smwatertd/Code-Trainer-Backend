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
    if _is_structural_program(lines):
        return _normalize_program_code("\n".join(line.strip() for line in lines if line.strip()))
    body_lines = [
        f"{line_prefix}{line}" if line_prefix and not line.startswith(line_prefix) else line for line in lines
    ]
    body = template["joiner"].join(body_lines)
    return f'{template["header"]}{body}{template["footer"]}'


def _normalize_program_code(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _is_structural_program(lines: list[str]) -> bool:
    joined = " ".join(line.strip().lower() for line in lines if line.strip())
    if (
        "program " in joined
        or joined.startswith("begin")
        or "#include" in joined
        or "public class" in joined
        or "using system" in joined
    ):
        return True
    # Pascal fragments from TC42 seeds: var ... begin ... end.
    return "begin" in joined and ("end." in joined or "end;" in joined)


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


def _statements_from_example_code(code: str) -> list[str]:
    return [
        line.rstrip()
        for line in code.splitlines()
        if line.strip()
    ]


def _blocks_match_language_paradigm(lines: list[str], language_id: str) -> bool:
    structural = _is_structural_program(lines)
    joined = "\n".join(lines).lower()

    if language_id == "python":
        return not structural
    if language_id == "pascal":
        joined = "\n".join(lines).lower()
        return "program " in joined or "begin" in joined or joined.lstrip().startswith("var ")
    if language_id == "cpp":
        return not structural or "#include" in joined
    if language_id == "java":
        return not structural or "public class" in joined
    if language_id == "csharp":
        return not structural or "using system" in joined
    return True


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
            localized = [localize_block_statement(str(item), language_id) for item in raw]
            if _blocks_match_language_paradigm(localized, language_id):
                return localized

    base = _base_block_statements(payload)
    localized = [localize_block_statement(line, language_id) for line in base]
    if _blocks_match_language_paradigm(localized, language_id):
        return localized

    examples = payload.get("code_examples")
    if isinstance(examples, dict):
        example = examples.get(language_id)
        if isinstance(example, str) and example.strip():
            return _statements_from_example_code(example)

    return localized


def resolve_block_reorder_correct_order(
    payload: dict[str, Any],
    language_id: str,
    statements: list[str] | None = None,
) -> list[int]:
    stored = list(payload.get("correct_order") or [])
    lines = statements if statements is not None else block_reorder_statements(payload, language_id)
    if not lines:
        return stored
    if len(stored) == len(lines):
        return stored
    return list(range(len(lines)))


def resolve_expected_block_reorder_code(
    payload: dict[str, Any],
    language_id: str,
    *,
    order: list[int] | None = None,
) -> str:
    statements = block_reorder_statements(payload, language_id)
    resolved_order = order or resolve_block_reorder_correct_order(payload, language_id, statements)
    if resolved_order and statements:
        return assemble_block_reorder_code(statements, resolved_order, language_id)

    by_language = payload.get("expected_code_by_language")
    if isinstance(by_language, dict) and language_id in by_language:
        return str(by_language[language_id])

    return str(payload.get("expected_code") or "")
