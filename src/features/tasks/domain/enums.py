from __future__ import annotations

from enum import StrEnum


class TaskFamily(StrEnum):
    TRANSLATION = "translation"
    BLOCK_REORDER = "block_reorder"
    FLOWCHART = "flowchart"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


_LEGACY_TASK_TYPE_TO_FAMILY: dict[str, TaskFamily] = {
    "translation": TaskFamily.TRANSLATION,
    "algorithm": TaskFamily.TRANSLATION,
    "task_write_from_description": TaskFamily.TRANSLATION,
    "block_reorder": TaskFamily.BLOCK_REORDER,
    "task_build_from_blocks": TaskFamily.BLOCK_REORDER,
    "diagram": TaskFamily.FLOWCHART,
    "task_flowchart_to_code": TaskFamily.FLOWCHART,
}


WRITE_FROM_DESCRIPTION_TASK_TYPES = frozenset({"task_write_from_description", "algorithm"})


def is_write_from_description_task(raw: str) -> bool:
    return raw.strip().lower() in WRITE_FROM_DESCRIPTION_TASK_TYPES


def task_family_from_legacy_type(raw: str) -> TaskFamily | None:
    return _LEGACY_TASK_TYPE_TO_FAMILY.get(raw.strip().lower())
