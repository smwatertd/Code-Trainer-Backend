from __future__ import annotations

from typing import Any

from src.shared.execution.checking.code_runner import CodeRunner
from src.shared.execution.checking.student_execution_errors import SEMANTIC_TEST_FAILED


def has_runnable_code(code: str) -> bool:
    stripped = code.strip()
    return bool(stripped) and stripped != "."


def build_semantic_test_result(
    *,
    code_runner: CodeRunner,
    language_id: str,
    code: str,
    test_cases: list[dict[str, Any]],
) -> dict[str, object]:
    raw = code_runner.run_tests(language_id, code, test_cases)
    test_results = [item.to_dict() for item in raw]
    tests_passed = bool(test_results) and all(item.get("status") == "PASSED" for item in test_results)

    if tests_passed:
        return {
            "success": True,
            "semantic_checked": True,
            "compiler_errors": [],
            "linter_errors": [],
            "pattern_errors": [],
            "test_results": test_results,
        }

    first_failed = next((item for item in test_results if item.get("status") != "PASSED"), None)
    message = (first_failed or {}).get("message") or SEMANTIC_TEST_FAILED
    return {
        "success": False,
        "semantic_checked": True,
        "compiler_errors": [{"type": "SEMANTIC", "text": message}],
        "linter_errors": [],
        "pattern_errors": [],
        "test_results": test_results,
    }
