from __future__ import annotations

from typing import Any, Protocol

from src.shared.execution.checking.dto import TestCaseResult


class CodeRunner(Protocol):
    def compile_check(self, language_id: str, code: str) -> list[str]: ...

    def lint(self, language_id: str, code: str) -> list[str]: ...

    def run_tests(self, language_id: str, code: str, test_cases: list[dict[str, Any]]) -> list[TestCaseResult]: ...
