from __future__ import annotations

import re
from typing import Any

from src.features.tasks.domain.block_reorder_language import BLOCK_REORDER_TEMPLATES

FLOWCHART_LANGUAGES = ("python", "cpp", "pascal", "java", "csharp")

_FOR_RANGE = re.compile(r"^for\s+(\w+)\s+in\s+range\((\d+)\):\s*$")
_FOR_RANGE_START = re.compile(r"^for\s+(\w+)\s+in\s+range\((\d+),\s*(\d+)\):\s*$")
_WHILE = re.compile(r"^while\s+(.+):\s*$")
_IF = re.compile(r"^if\s+(.+):\s*$")
_ELSE = re.compile(r"^else:\s*$")
_ASSIGN_INPUT = re.compile(r"^(\w+)\s*=\s*input\(\)\s*$")
_ASSIGN_INT_INPUT = re.compile(r"^(\w+)\s*=\s*int\(input\(\)\)\s*$")
_ASSIGN = re.compile(r"^(\w+)\s*=\s*(.+)$")
_PRINT = re.compile(r"^print\((.+)\)\s*$")
_DEF = re.compile(r"^def\s+(\w+)\(\):\s*$")
_RETURN = re.compile(r"^return\s+(.+)$")
_AUG_SUB = re.compile(r"^(\w+)\s*-\=\s*(\d+)\s*$")


def _pad(line: str, depth: int, language_id: str) -> str:
    if language_id == "pascal":
        return f"{'  ' * depth}{line}"
    return f"{'    ' * depth}{line}"


def _close_block(depth: int, language_id: str) -> str:
    if language_id == "pascal":
        return _pad("end;", depth - 1, language_id)
    return _pad("}", depth - 1, language_id)


def _quote_expr(expr: str, language_id: str) -> str:
    expr = expr.strip()
    if (expr.startswith("'") and expr.endswith("'")) or (expr.startswith('"') and expr.endswith('"')):
        inner = expr[1:-1]
        if language_id == "pascal":
            return f"'{inner}'"
        return f'"{inner}"'
    return expr


def _print_line(expr: str, language_id: str) -> str:
    value = _quote_expr(expr, language_id)
    if language_id == "cpp":
        return f"cout << {value} << endl;"
    if language_id == "pascal":
        return f"WriteLn({value});"
    if language_id == "java":
        return f"System.out.println({value});"
    if language_id == "csharp":
        return f"Console.WriteLine({value});"
    return f"print({expr})"


def _input_line(name: str, language_id: str, *, as_int: bool = False) -> str:
    if language_id == "cpp":
        if as_int:
            return f"int {name}; cin >> {name};"
        return f"string {name}; cin >> {name};"
    if language_id == "pascal":
        return f"ReadLn({name});"
    if language_id == "java":
        if as_int:
            return f"int {name} = scanner.nextInt();"
        return f"String {name} = scanner.nextLine();"
    if language_id == "csharp":
        if as_int:
            return f"int {name} = int.Parse(Console.ReadLine());"
        return f"string {name} = Console.ReadLine();"
    if as_int:
        return f"{name} = int(input())"
    return f"{name} = input()"


def _translate_statement(line: str, language_id: str) -> tuple[str, bool]:
    if language_id == "python":
        return line, line.endswith(":")

    match = _DEF.match(line)
    if match:
        name = match.group(1)
        if language_id == "cpp":
            return f"string {name}() {{", True
        if language_id == "pascal":
            return f"function {name}: string; begin", True
        if language_id == "java":
            return f"static String {name}() {{", True
        if language_id == "csharp":
            return f"static string {name}() {{", True

    match = _RETURN.match(line)
    if match:
        value = _quote_expr(match.group(1), language_id)
        if language_id == "pascal":
            return f"Result := {value};", False
        if language_id in {"cpp", "java", "csharp"}:
            return f"return {value};", False

    match = _FOR_RANGE.match(line)
    if match:
        var, upper = match.group(1), match.group(2)
        if language_id == "cpp":
            return f"for (int {var} = 0; {var} < {upper}; {var}++) {{", True
        if language_id == "pascal":
            return f"for {var} := 0 to {int(upper) - 1} do begin", True
        if language_id == "java":
            return f"for (int {var} = 0; {var} < {upper}; {var}++) {{", True
        if language_id == "csharp":
            return f"for (int {var} = 0; {var} < {upper}; {var}++) {{", True

    match = _FOR_RANGE_START.match(line)
    if match:
        var, start, end = match.group(1), match.group(2), match.group(3)
        if language_id == "cpp":
            return f"for (int {var} = {start}; {var} < {end}; {var}++) {{", True
        if language_id == "pascal":
            return f"for {var} := {start} to {int(end) - 1} do begin", True
        if language_id == "java":
            return f"for (int {var} = {int(start)}; {var} < {end}; {var}++) {{", True
        if language_id == "csharp":
            return f"for (int {var} = {int(start)}; {var} < {end}; {var}++) {{", True

    match = _WHILE.match(line)
    if match:
        cond = match.group(1)
        if language_id == "cpp":
            return f"while ({cond}) {{", True
        if language_id == "pascal":
            return f"while {cond} do begin", True
        if language_id == "java":
            return f"while ({cond}) {{", True
        if language_id == "csharp":
            return f"while ({cond}) {{", True

    match = _IF.match(line)
    if match:
        cond = match.group(1)
        if language_id == "cpp":
            return f"if ({cond}) {{", True
        if language_id == "pascal":
            return f"if {cond} then begin", True
        if language_id == "java":
            return f"if ({cond}) {{", True
        if language_id == "csharp":
            return f"if ({cond}) {{", True

    if _ELSE.match(line):
        if language_id == "cpp":
            return "} else {", True
        if language_id == "pascal":
            return "end else begin", True
        if language_id == "java":
            return "} else {", True
        if language_id == "csharp":
            return "} else {", True

    match = _ASSIGN_INT_INPUT.match(line)
    if match:
        return _input_line(match.group(1), language_id, as_int=True), False

    match = _ASSIGN_INPUT.match(line)
    if match:
        return _input_line(match.group(1), language_id), False

    match = _PRINT.match(line)
    if match:
        return _print_line(match.group(1), language_id), False

    match = _AUG_SUB.match(line)
    if match:
        name, value = match.group(1), match.group(2)
        if language_id == "cpp":
            return f"{name} -= {value};", False
        if language_id == "pascal":
            return f"{name} := {name} - {value};", False
        if language_id == "java":
            return f"{name} -= {value};", False
        if language_id == "csharp":
            return f"{name} -= {value};", False

    match = _ASSIGN.match(line)
    if match:
        name, expr = match.group(1), match.group(2)
        if language_id == "cpp":
            return f"{name} = {expr};", False
        if language_id == "pascal":
            return f"{name} := {expr};", False
        if language_id == "java":
            return f"{name} = {expr};", False
        if language_id == "csharp":
            return f"{name} = {expr};", False

    return line, False


def localize_flowchart_source(source: str, language_id: str) -> str:
    if language_id == "python":
        return source

    template = BLOCK_REORDER_TEMPLATES.get(language_id, BLOCK_REORDER_TEMPLATES["python"])
    lines = [line for line in source.splitlines() if line.strip()]
    body: list[str] = []
    indent_stack = [0]

    for raw in lines:
        stripped = raw.strip()
        indent = len(raw) - len(stripped)

        while indent < indent_stack[-1]:
            indent_stack.pop()
            body.append(_close_block(len(indent_stack), language_id))

        converted, opens = _translate_statement(stripped, language_id)
        body.append(_pad(converted, len(indent_stack), language_id))
        if opens:
            indent_stack.append(indent + 4)

    while len(indent_stack) > 1:
        indent_stack.pop()
        body.append(_close_block(len(indent_stack), language_id))

    if language_id == "java" and any("scanner." in line for line in body):
        body.insert(0, _pad("Scanner scanner = new Scanner(System.in);", 0, language_id))
        header = "import java.util.Scanner;\n\n" + template["header"]
    else:
        header = template["header"]

    joined = "\n".join(body)
    footer = template["footer"]
    return f"{header}{joined}{footer}"


def synthesize_flowchart_source_by_language(source: str) -> dict[str, str]:
    return {language_id: localize_flowchart_source(source, language_id) for language_id in FLOWCHART_LANGUAGES}


def resolve_flowchart_reference_code(payload: dict[str, Any], language_id: str) -> str:
    variants = payload.get("source_code_by_language")
    if isinstance(variants, dict):
        raw = variants.get(language_id)
        if isinstance(raw, str) and raw.strip():
            return raw

    base = str(payload.get("source_code") or "")
    if not base.strip():
        return ""
    return localize_flowchart_source(base, language_id)
