from __future__ import annotations

from typing import Any

from src.core.either import AppResult
from src.features.tasks.domain.block_reorder_language import resolve_expected_block_reorder_code
from src.features.tasks.services.block_reorder_validator import validate_block_order_structure
from src.shared.execution.checking.code_runner import CodeRunner
from src.shared.execution.checking.semantic_test_runner import build_semantic_test_result
from src.shared.execution.checking.student_execution_errors import BLOCKS_WRONG_ORDER
from src.shared.execution.checking.task_metadata import task_test_cases


class BlockReorderPipeline:
    def __init__(self, code_runner: CodeRunner) -> None:
        self._code_runner = code_runner

    def run(
        self,
        *,
        language_id: str,
        code: str,
        task_payload: dict[str, Any],
        block_order: list[int],
    ) -> dict[str, object]:
        correct_order = list(task_payload.get("correct_order") or [])
        expected_code = resolve_expected_block_reorder_code(task_payload, language_id)

        validation = validate_block_order_structure(
            submitted_order=block_order,
            correct_order=correct_order,
            assembled_code=code,
            expected_code=expected_code,
        )
        if validation.is_err():
            return self._structural_failure(validation)

        test_cases = task_test_cases(task_payload)
        if not test_cases:
            return self._structural_success()

        return self._run_semantic_tests(language_id=language_id, code=code, test_cases=test_cases)

    @staticmethod
    def _structural_failure(validation: AppResult[None]) -> dict[str, object]:
        message = validation.error.message if validation.is_err() else BLOCKS_WRONG_ORDER
        return {
            "success": False,
            "semantic_checked": False,
            "compiler_errors": [{"type": "VALIDATION", "text": message}],
            "linter_errors": [],
            "pattern_errors": [],
            "test_results": [],
        }

    @staticmethod
    def _structural_success() -> dict[str, object]:
        return {
            "success": True,
            "semantic_checked": False,
            "compiler_errors": [],
            "linter_errors": [],
            "pattern_errors": [],
            "test_results": [],
        }

    def _run_semantic_tests(
        self,
        *,
        language_id: str,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> dict[str, object]:
        return build_semantic_test_result(
            code_runner=self._code_runner,
            language_id=language_id,
            code=code,
            test_cases=test_cases,
        )
