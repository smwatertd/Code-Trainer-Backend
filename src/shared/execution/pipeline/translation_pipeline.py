from __future__ import annotations

from typing import Any

from src.shared.execution.checking.code_runner import CodeRunner
from src.shared.execution.checking.pattern_checker import PatternChecker
from src.shared.execution.checking.task_metadata import (
    is_snippet_translation_task,
    task_constructions,
    task_test_cases,
)


class TranslationPipeline:
    def __init__(
        self,
        code_runner: CodeRunner,
        pattern_checker: PatternChecker | None = None,
    ) -> None:
        self._code_runner = code_runner
        self._pattern_checker = pattern_checker or PatternChecker()

    def run(
        self,
        *,
        language_id: str,
        code: str,
        task_type: str,
        task_payload: dict[str, Any],
        mode: str = "full",
    ) -> dict[str, object]:
        normalized_mode = (mode or "full").lower()
        test_cases = task_test_cases(task_payload)
        constructions = task_constructions(task_payload)

        if test_cases:
            compiler_errors, linter_errors, pattern_errors = self._run_checks(
                language_id,
                code,
                constructions,
                mode="full",
            )
            test_results = self._run_tests(
                language_id,
                code,
                test_cases,
                has_compiler_errors=bool(compiler_errors),
            )
            semantic_required = True
        elif is_snippet_translation_task(task_type, task_payload):
            compiler_errors, linter_errors, pattern_errors = self._run_checks(
                language_id,
                code,
                constructions,
                mode="pattern_only",
            )
            test_results = []
            semantic_required = False
        else:
            compiler_errors, linter_errors, pattern_errors = self._run_checks(
                language_id,
                code,
                constructions,
                mode=normalized_mode,
            )
            test_results = []
            semantic_required = normalized_mode == "full"

        return self._build_result(
            compiler_errors=compiler_errors,
            linter_errors=linter_errors,
            pattern_errors=pattern_errors,
            test_results=test_results,
            semantic_required=semantic_required,
        )

    def _run_checks(
        self,
        language_id: str,
        code: str,
        constructions: list[Any],
        *,
        mode: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        run_compiler = mode in {"full", "compile_only"}
        run_linter = mode in {"full", "lint_only"}
        run_pattern = mode in {"full", "pattern_only"}

        compiler_errors: list[dict[str, str]] = []
        linter_errors: list[dict[str, str]] = []
        if run_compiler:
            compiler_errors = self._as_errors(self._code_runner.compile_check(language_id, code), "COMPILER")
        if run_linter and not compiler_errors:
            linter_errors = self._as_errors(self._code_runner.lint(language_id, code), "LINTER")

        pattern_errors = self._run_pattern(code, language_id, constructions, run_pattern=run_pattern)
        return compiler_errors, linter_errors, pattern_errors

    def _run_pattern(
        self,
        code: str,
        language_id: str,
        constructions: list[Any],
        *,
        run_pattern: bool,
    ) -> list[dict[str, str]]:
        if not run_pattern:
            return []
        messages = self._pattern_checker.check(code, language_id, constructions)
        return self._as_errors(messages, "CONSTRUCTION")

    def _run_tests(
        self,
        language_id: str,
        code: str,
        test_cases: list[dict[str, Any]],
        *,
        has_compiler_errors: bool,
    ) -> list[dict[str, Any]]:
        if has_compiler_errors or not test_cases:
            return []
        raw = self._code_runner.run_tests(language_id, code, test_cases)
        return [item.to_dict() for item in raw]

    @staticmethod
    def _as_errors(messages: list[str], error_type: str) -> list[dict[str, str]]:
        return [{"type": error_type, "text": message} for message in messages if message]

    @staticmethod
    def _build_result(
        *,
        compiler_errors: list[dict[str, str]],
        linter_errors: list[dict[str, str]],
        pattern_errors: list[dict[str, str]],
        test_results: list[dict[str, Any]],
        semantic_required: bool = False,
    ) -> dict[str, object]:
        tests_passed = bool(test_results) and all(item.get("status") == "PASSED" for item in test_results)
        checks_ok = not compiler_errors and not pattern_errors
        if semantic_required:
            success = checks_ok and tests_passed
        else:
            success = checks_ok and (tests_passed if test_results else True)
        return {
            "success": success,
            "compiler_errors": compiler_errors,
            "linter_errors": linter_errors,
            "pattern_errors": pattern_errors,
            "test_results": test_results,
        }
