from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.shared.execution.checking.dto import TestCaseResult as CaseRunResult
from src.shared.execution.checking.semantic_test_runner import (
    build_semantic_test_result,
    has_runnable_code,
)


@dataclass
class _FakeCodeRunner:
    results: list[CaseRunResult]

    def compile_check(self, language_id: str, code: str) -> list[str]:
        return []

    def lint(self, language_id: str, code: str) -> list[str]:
        return []

    def run_tests(self, language_id: str, code: str, test_cases: list[dict[str, Any]]) -> list[CaseRunResult]:
        return list(self.results)


def test_has_runnable_code__rejects_placeholder() -> None:
    assert has_runnable_code(".") is False
    assert has_runnable_code("  ") is False
    assert has_runnable_code("print(1)") is True


def test_build_semantic_test_result__passes() -> None:
    result = build_semantic_test_result(
        code_runner=_FakeCodeRunner(results=[CaseRunResult(case=1, status="PASSED", expected="hi", actual="hi")]),
        language_id="python",
        code="print('hi')",
        test_cases=[{"inputs": "", "output": "hi"}],
    )

    assert result["success"] is True
    assert result["semantic_checked"] is True


def test_build_semantic_test_result__fails() -> None:
    result = build_semantic_test_result(
        code_runner=_FakeCodeRunner(results=[CaseRunResult(case=1, status="FAILED", message="wrong output")]),
        language_id="python",
        code="print('no')",
        test_cases=[{"inputs": "", "output": "hi"}],
    )

    assert result["success"] is False
    assert result["compiler_errors"][0]["type"] == "SEMANTIC"
