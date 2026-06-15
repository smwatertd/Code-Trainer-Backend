from __future__ import annotations

from typing import Any

from src.shared.analysis.construction_tag_detector import (
    is_tagged_construction,
    missing_construction_tag_labels,
)
from src.shared.analysis.educational_validator import EducationalValidator

_validator = EducationalValidator()
_PARSE_FAILURE_MESSAGE = "Не удалось разобрать код для проверки требуемых конструкций."


class PatternChecker:
    def check(self, code: str, language: str, expected_patterns: list[Any]) -> list[str]:
        if not expected_patterns:
            return []

        tagged = [str(item) for item in expected_patterns if is_tagged_construction(str(item))]
        concept_tags = [str(item) for item in expected_patterns if not is_tagged_construction(str(item))]

        messages: list[str] = []
        messages.extend(missing_construction_tag_labels(code, language, tagged))

        if concept_tags:
            try:
                messages.extend(_validator.missing_structure_labels(code, language, concept_tags))
            except Exception:
                messages.append(_PARSE_FAILURE_MESSAGE)

        seen: set[str] = set()
        unique: list[str] = []
        for message in messages:
            if message in seen:
                continue
            seen.add(message)
            unique.append(message)
        return unique
