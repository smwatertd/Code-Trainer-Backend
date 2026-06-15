from __future__ import annotations

import pytest

from migrations.seeds.tc42_course_catalog_generated import build_tc42_course_catalog
from src.core.either import Err, Ok
from src.features.tasks.domain.block_reorder_language import (
    assemble_block_reorder_code,
    block_reorder_statements,
    resolve_block_reorder_correct_order,
    resolve_expected_block_reorder_code,
)
from src.features.tasks.services.block_reorder_validator import validate_block_order_structure
from src.shared.execution.checking.dto import TestCaseResult as CaseRunResult
from src.shared.execution.pipeline.block_reorder_pipeline import BlockReorderPipeline
from src.shared.student_messages import ASSEMBLED_CODE_MISMATCH, BLOCKS_WRONG_ORDER


def _block_reorder_tasks() -> list[dict]:
    return [
        row["payload"]
        for row in build_tc42_course_catalog()
        if row.get("task_type") == "task_build_from_blocks"
    ]


def _fake_pipeline(*, semantic_pass: bool = True) -> BlockReorderPipeline:
    class _Runner:
        def compile_check(self, language_id: str, code: str) -> list[str]:
            return []

        def lint(self, language_id: str, code: str) -> list[str]:
            return []

        def run_tests(
            self,
            language_id: str,
            code: str,
            test_cases: list[dict[str, object]],
        ) -> list[CaseRunResult]:
            if not semantic_pass:
                return []
            return [
                CaseRunResult(
                    case=index + 1,
                    status="PASSED",
                    inputs=str(test_case.get("inputs", "")),
                    expected=str(test_case.get("output", "")),
                    actual=str(test_case.get("output", "")),
                    message="",
                )
                for index, test_case in enumerate(test_cases)
            ]

    return BlockReorderPipeline(_Runner())


_BLOCK_TASK_IDS = [1, 5, 9, 13]


@pytest.mark.parametrize(
    "payload",
    [t["payload"] for t in build_tc42_course_catalog() if t["id"] in _BLOCK_TASK_IDS],
    ids=[f"task-{task_id}" for task_id in _BLOCK_TASK_IDS],
)
def test_seed_block_tasks__assembled_code_matches_expected_from_blocks(payload: dict) -> None:
    language_id = str(payload["language"])
    statements = block_reorder_statements(payload, language_id)
    correct_order = resolve_block_reorder_correct_order(payload, language_id, statements)

    assembled = assemble_block_reorder_code(statements, correct_order, language_id)
    expected = resolve_expected_block_reorder_code(payload, language_id, order=correct_order)

    assert assembled == expected


@pytest.mark.parametrize(
    "payload",
    [t["payload"] for t in build_tc42_course_catalog() if t["id"] in _BLOCK_TASK_IDS],
    ids=[f"task-{task_id}" for task_id in _BLOCK_TASK_IDS],
)
def test_seed_block_tasks__validation_accepts_assembled_code(payload: dict) -> None:
    language_id = str(payload["language"])
    statements = block_reorder_statements(payload, language_id)
    correct_order = resolve_block_reorder_correct_order(payload, language_id, statements)
    code = assemble_block_reorder_code(statements, correct_order, language_id)
    expected = resolve_expected_block_reorder_code(payload, language_id, order=correct_order)

    result = validate_block_order_structure(
        submitted_order=correct_order,
        correct_order=correct_order,
        assembled_code=code,
        expected_code=expected,
    )

    assert isinstance(result, Ok)


@pytest.mark.parametrize(
    "payload",
    [t["payload"] for t in build_tc42_course_catalog() if t["id"] in _BLOCK_TASK_IDS],
    ids=[f"task-{task_id}" for task_id in _BLOCK_TASK_IDS],
)
def test_seed_block_tasks__pipeline_accepts_assembled_code(payload: dict) -> None:
    language_id = str(payload["language"])
    statements = block_reorder_statements(payload, language_id)
    correct_order = resolve_block_reorder_correct_order(payload, language_id, statements)
    code = assemble_block_reorder_code(statements, correct_order, language_id)

    result = _fake_pipeline().run(
        language_id=language_id,
        code=code,
        task_payload=payload,
        block_order=correct_order,
    )

    assert result["success"] is True
    assert result["semantic_checked"] is True


def test_seed_block_task__legacy_expected_code_mismatch_is_rejected() -> None:
    payload = _block_reorder_tasks()[0]
    statements = block_reorder_statements(payload, "pascal")
    correct_order = resolve_block_reorder_correct_order(payload, "pascal", statements)
    assembled = assemble_block_reorder_code(statements, correct_order, "pascal")
    legacy_expected = str(payload["expected_code"])

    result = validate_block_order_structure(
        submitted_order=correct_order,
        correct_order=correct_order,
        assembled_code=assembled,
        expected_code=legacy_expected,
    )

    assert isinstance(result, Err)
    assert result.error.message == ASSEMBLED_CODE_MISMATCH


def test_seed_block_task__python_path_resolves_blocks_from_examples() -> None:
    payload = _block_reorder_tasks()[0]
    statements = block_reorder_statements(payload, "python")
    correct_order = resolve_block_reorder_correct_order(payload, "python", statements)
    code = assemble_block_reorder_code(statements, correct_order, "python")

    assert len(statements) >= 1
    assert len(correct_order) == len(statements)

    validation = validate_block_order_structure(
        submitted_order=correct_order,
        correct_order=correct_order,
        assembled_code=code,
        expected_code=resolve_expected_block_reorder_code(payload, "python", order=correct_order),
    )
    assert isinstance(validation, Ok)


def test_block_reorder_pipeline__rejects_wrong_order_before_code_mismatch() -> None:
    payload = _block_reorder_tasks()[0]
    statements = block_reorder_statements(payload, "pascal")
    correct_order = resolve_block_reorder_correct_order(payload, "pascal", statements)
    code = assemble_block_reorder_code(statements, correct_order, "pascal")

    result = _fake_pipeline(semantic_pass=False).run(
        language_id="pascal",
        code=code,
        task_payload=payload,
        block_order=list(reversed(correct_order)),
    )

    assert result["success"] is False
    assert result["semantic_checked"] is False
    assert result["compiler_errors"][0]["text"] == BLOCKS_WRONG_ORDER
