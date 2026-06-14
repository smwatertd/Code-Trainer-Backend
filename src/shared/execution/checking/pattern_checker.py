from __future__ import annotations

from typing import Any

from src.shared.analysis.educational_validator import EducationalValidator

_validator = EducationalValidator()
_PARSE_FAILURE_MESSAGE = "Не удалось разобрать код для проверки требуемых конструкций."


class PatternChecker:
    def check(self, code: str, language: str, expected_patterns: list[Any]) -> list[str]:
        if not expected_patterns:
            return []
        try:
            return _validator.missing_structure_labels(code, language, expected_patterns)
        except Exception:
            return [_PARSE_FAILURE_MESSAGE]
