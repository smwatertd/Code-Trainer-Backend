from __future__ import annotations

import re
from typing import Any

_FOR_RANGE = re.compile(r"for\s+\w+\s+in\s+range\s*\(\s*([^)]+)\s*\)", re.IGNORECASE)
_WHILE = re.compile(r"while\s+([^:]+):", re.IGNORECASE)
_IF = re.compile(r"if\s+([^:]+):", re.IGNORECASE)
_PRINT = re.compile(r"print\s*\(\s*([^)]+)\s*\)", re.IGNORECASE)
_ASSIGN = re.compile(r"^(\w+)\s*=\s*(.+)$")
_AUG_SUB = re.compile(r"^(\w+)\s*-=\s*(\d+)\s*$")
_DEF = re.compile(r"^def\s+(\w+)\s*\(", re.IGNORECASE)
_INPUT = re.compile(r"input\s*\(\s*\)", re.IGNORECASE)
_INT_INPUT = re.compile(r"int\s*\(\s*input\s*\(\s*\)\s*\)", re.IGNORECASE)


def normalize_flow_text(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


_READLN = re.compile(r"readln\s*\(\s*(\w+)\s*\)", re.IGNORECASE)
_WRITELN = re.compile(r"writeln\s*\(\s*([^)]+)\s*\)", re.IGNORECASE)


def block_text_for_matching(text: str) -> str:
    """Normalize block text and expand flowchart notation (readln/writeln) for alignment checks."""
    expanded = normalize_flow_text(text)

    readln_match = _READLN.search(text)
    if readln_match:
        expanded += "intinput"
        expanded += normalize_flow_text(readln_match.group(1))

    for match in _WRITELN.finditer(text):
        argument = match.group(1).strip()
        quoted = re.match(r"^(['\"])(.+)\1$", argument)
        if quoted:
            expanded += normalize_flow_text(quoted.group(2))
        else:
            expanded += normalize_flow_text(argument)

    return expanded


_DECREMENT_AUG = re.compile(r"^(\w+)\s*-\=\s*(\d+)\s*;?$", re.IGNORECASE)
_DECREMENT_ASSIGN = re.compile(
    r"^(\w+)\s*[:=]\s*\1\s*-\s*(\d+)\s*;?$",
    re.IGNORECASE,
)


def decrement_equivalent_fragments(var_name: str, delta: str) -> set[str]:
    var = var_name.lower()
    amount = normalize_flow_text(delta)
    return {
        normalize_flow_text(f"{var}-={amount}"),
        normalize_flow_text(f"{var}={var}-{amount}"),
        normalize_flow_text(f"{var}:={var}-{amount}"),
    }


def expand_block_text_aliases(text: str) -> str:
    expanded = normalize_flow_text(text)
    for pattern in (_DECREMENT_AUG, _DECREMENT_ASSIGN):
        match = pattern.match(text.strip())
        if match:
            expanded += "".join(decrement_equivalent_fragments(match.group(1), match.group(2)))
            break

    lowered = text.lower()
    if "writeln" in lowered or "cout" in lowered or "system.out" in lowered or "console.write" in lowered:
        expanded += "print"
    if "readln" in lowered or "cin" in lowered or "scanner." in lowered or "console.readline" in lowered:
        expanded += "input"
    return expanded


def block_text_matches_fragments(text: str, fragments: list[str]) -> bool:
    expanded = expand_block_text_aliases(block_text_for_matching(text))
    if all(fragment in expanded for fragment in fragments):
        return True

    if len(fragments) == 1:
        fragment = fragments[0]
        aug = re.match(r"^(\w+)-=(\d+)$", fragment)
        if aug:
            return any(item in expanded for item in decrement_equivalent_fragments(aug.group(1), aug.group(2)))

    return False


def _range_fragment(inner: str) -> str:
    cleaned = re.sub(r"\s+", "", inner.lower())
    return f"range({cleaned})"


def extract_text_requirements(source_code: str) -> list[dict[str, Any]]:
    """Derive required block text fragments from canonical Python source."""
    requirements: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()

    def add(
        *,
        block_types: list[str],
        contains_all: list[str],
        hint: str,
    ) -> None:
        key = (",".join(block_types), tuple(contains_all))
        if key in seen:
            return
        seen.add(key)
        requirements.append(
            {
                "block_types": block_types,
                "contains_all": contains_all,
                "hint": hint,
            }
        )

    for match in _FOR_RANGE.finditer(source_code):
        inner = match.group(1)
        fragment = _range_fragment(inner)
        add(
            block_types=["loop"],
            contains_all=[fragment],
            hint=f"В блоке «Цикл» укажите условие {fragment}, как в программе.",
        )

    for match in _WHILE.finditer(source_code):
        condition = normalize_flow_text(match.group(1))
        add(
            block_types=["loop"],
            contains_all=[condition],
            hint=f"В блоке «Цикл» укажите условие «{match.group(1).strip()}», как в программе.",
        )

    for match in _IF.finditer(source_code):
        condition = normalize_flow_text(match.group(1))
        add(
            block_types=["decision"],
            contains_all=[condition],
            hint=f"В блоке «Условие» укажите проверку «{match.group(1).strip()}», как в программе.",
        )

    for match in _PRINT.finditer(source_code):
        argument = match.group(1).strip()
        arg_norm = normalize_flow_text(argument)
        quoted = re.match(r"^(['\"])(.+)\1$", argument)
        if quoted:
            literal = quoted.group(2).lower()
            add(
                block_types=["output"],
                contains_all=[literal],
                hint=f"В блоке «Вывод» укажите текст «{quoted.group(2)}», как в программе.",
            )
        elif re.search(r"[\+\-\*/]", argument):
            add(
                block_types=["process"],
                contains_all=[arg_norm],
                hint=f"В блоке «Процесс» укажите выражение «{argument}», как в программе.",
            )
            add(
                block_types=["output"],
                contains_all=["print"],
                hint="В блоке «Вывод» укажите операцию вывода (print), как в программе.",
            )
        else:
            add(
                block_types=["output"],
                contains_all=[arg_norm],
                hint=f"В блоке «Вывод» укажите выражение «{argument}», как в программе.",
            )

    for line in source_code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("for ", "while ", "if ", "else")):
            continue

        if _DEF.match(stripped):
            name = _DEF.match(stripped).group(1).lower()
            add(
                block_types=["process"],
                contains_all=[name],
                hint=f"В блоке «Процесс» укажите функцию «{name}», как в программе.",
            )
            continue

        aug = _AUG_SUB.match(stripped)
        if aug:
            add(
                block_types=["process"],
                contains_all=[normalize_flow_text(stripped)],
                hint=f"В блоке «Действие» укажите операцию «{stripped}» (или эквивалент, например n = n - 1), как в программе.",
            )
            continue

        assign = _ASSIGN.match(stripped)
        if assign and _INT_INPUT.search(stripped):
            add(
                block_types=["input"],
                contains_all=["int", "input"],
                hint="В блоке «Ввод» укажите чтение целого числа, как в программе.",
            )
            continue

        if assign and _INPUT.search(stripped):
            add(
                block_types=["input"],
                contains_all=["input"],
                hint="В блоке «Ввод» укажите операцию ввода, как в программе.",
            )
            continue

        if assign and "+" in stripped and "input" not in stripped.lower():
            add(
                block_types=["process"],
                contains_all=["+"],
                hint="В блоке «Процесс» укажите сложение, как в программе.",
            )
            continue

        if assign and "*" in stripped:
            add(
                block_types=["process"],
                contains_all=["*"],
                hint="В блоке «Процесс» укажите умножение, как в программе.",
            )
            continue

        if assign:
            rhs = assign.group(2)
            if "+" in rhs and assign.group(1) == rhs.split("+")[0].strip():
                add(
                    block_types=["process"],
                    contains_all=[normalize_flow_text(stripped)],
                    hint=f"В блоке «Процесс» укажите «{stripped}», как в программе.",
                )

    return requirements


def validate_flowchart_source_alignment(
    nodes: list[dict[str, Any]],
    source_code: str,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    if not source_code.strip():
        return [], []

    requirements = extract_text_requirements(source_code)
    if not requirements:
        return [], []

    errors: list[dict[str, str]] = []
    failures: list[dict[str, Any]] = []
    matched_ids: set[str] = set()

    for requirement in requirements:
        block_types = requirement["block_types"]
        contains_all = [normalize_flow_text(item) for item in requirement["contains_all"]]

        matched = False
        for node in nodes:
            node_id = str(node["id"])
            if node_id in matched_ids:
                continue
            if node["type"] not in block_types:
                continue
            if block_text_matches_fragments(str(node.get("text") or ""), contains_all):
                matched_ids.add(node_id)
                matched = True
                break

        if not matched:
            errors.append(
                {
                    "type": "FLOW_SOURCE_MISMATCH",
                    "text": requirement["hint"],
                }
            )
            failures.append(requirement)

    return errors, failures
