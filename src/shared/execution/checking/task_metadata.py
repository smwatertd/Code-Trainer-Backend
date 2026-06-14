from __future__ import annotations

from typing import Any


def task_constructions(task_payload: dict[str, Any]) -> list[Any]:
    required = task_payload.get("required_structures")
    if isinstance(required, list) and required:
        return required
    constructions = task_payload.get("constructions")
    if isinstance(constructions, list):
        return constructions
    return []


def task_test_cases(task_payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = task_payload.get("test_cases")
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    return []


def is_snippet_translation_task(task_type: str, task_payload: dict[str, Any]) -> bool:
    if task_type == "task_translate_snippet":
        return True
    return str(task_payload.get("kind") or "").strip() == "snippet"
