from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.shared.execution.checking.flow_student_messages import student_flow_error_text

BLOCK_TYPE_LABELS_RU: dict[str, str] = {
    "start": "Начало",
    "input": "Ввод",
    "process": "Действие",
    "decision": "Условие",
    "loop": "Цикл",
    "output": "Вывод",
    "end": "Конец",
}

DEFAULT_ALLOWED_BLOCKS: tuple[str, ...] = (
    "start",
    "input",
    "process",
    "decision",
    "loop",
    "output",
    "end",
)


@dataclass(frozen=True)
class ConstructionBlockRule:
    block_types: frozenset[str]
    min_count: int = 1
    require_all_types: bool = False
    match_any_type: bool = False
    label_ru: str = ""


CONSTRUCTION_BLOCK_RULES: dict[str, ConstructionBlockRule] = {
    "if_statement": ConstructionBlockRule(
        block_types=frozenset({"decision"}),
        label_ru="ветвление (блок «Условие»)",
    ),
    "condition": ConstructionBlockRule(
        block_types=frozenset({"decision"}),
        label_ru="ветвление (блок «Условие»)",
    ),
    "cond": ConstructionBlockRule(
        block_types=frozenset({"decision"}),
        label_ru="ветвление (блок «Условие»)",
    ),
    "for_loop": ConstructionBlockRule(
        block_types=frozenset({"loop"}),
        label_ru="цикл (блок «Цикл»)",
    ),
    "while_loop": ConstructionBlockRule(
        block_types=frozenset({"loop"}),
        label_ru="цикл (блок «Цикл»)",
    ),
    "function_definition": ConstructionBlockRule(
        block_types=frozenset({"process"}),
        label_ru="определение функции (блок «Действие»)",
    ),
    "loop": ConstructionBlockRule(
        block_types=frozenset({"loop"}),
        label_ru="цикл (блок «Цикл»)",
    ),
    "nested_loops": ConstructionBlockRule(
        block_types=frozenset({"loop"}),
        min_count=2,
        label_ru="вложенные циклы (два блока «Цикл»)",
    ),
    "io": ConstructionBlockRule(
        block_types=frozenset({"input", "output"}),
        require_all_types=True,
        label_ru="ввод и вывод (блоки «Ввод» и «Вывод»)",
    ),
}


def label_block_type(block_type: str) -> str:
    return BLOCK_TYPE_LABELS_RU.get(block_type, block_type)


def format_sequence_labels(sequence: list[str]) -> str:
    return " → ".join(label_block_type(item) for item in sequence)


def validate_constructions_from_blocks(
    *,
    submitted_types: list[str],
    constructions: list[Any],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    debug_items: list[dict[str, str]] = []
    seen_tags: set[str] = set()

    for raw in constructions:
        tag = str(raw or "").strip().lower()
        if not tag or tag in seen_tags:
            continue
        seen_tags.add(tag)

        rule = CONSTRUCTION_BLOCK_RULES.get(tag)
        if rule is None:
            continue

        if rule.require_all_types:
            missing = [item for item in rule.block_types if item not in submitted_types]
            if missing:
                errors.append(
                    {
                        "type": "FLOW_CONSTRUCTION_MISSING",
                        "text": student_flow_error_text("FLOW_CONSTRUCTION_MISSING"),
                    }
                )
                debug_items.append(
                    {
                        "construction": tag,
                        "missing": rule.label_ru,
                        "missing_block_types": ", ".join(sorted(missing)),
                    }
                )
            continue

        if rule.match_any_type:
            count = sum(submitted_types.count(block_type) for block_type in rule.block_types)
        else:
            primary_type = next(iter(rule.block_types))
            count = submitted_types.count(primary_type)
        if count < rule.min_count:
            errors.append(
                {
                    "type": "FLOW_CONSTRUCTION_MISSING",
                    "text": student_flow_error_text("FLOW_CONSTRUCTION_MISSING"),
                }
            )
            debug_items.append(
                {
                    "construction": tag,
                    "missing": rule.label_ru,
                    "required_count": str(rule.min_count),
                    "found_count": str(count),
                }
            )

    return errors, debug_items
