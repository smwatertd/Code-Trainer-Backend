from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.shared.execution.checking.dto import TestCaseResult as CaseRunResult
from src.shared.execution.pipeline.block_reorder_pipeline import BlockReorderPipeline


@dataclass
class _FakeCodeRunner:
    results: list[CaseRunResult]

    def compile_check(self, language_id: str, code: str) -> list[str]:
        return []

    def lint(self, language_id: str, code: str) -> list[str]:
        return []

    def run_tests(self, language_id: str, code: str, test_cases: list[dict[str, Any]]) -> list[CaseRunResult]:
        return list(self.results)


def _task_payload(*, with_tests: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {
        "correct_order": [1, 0],
        "expected_code": "print('b')\nprint('a')",
    }
    if with_tests:
        payload["test_cases"] = [{"inputs": "", "output": "b\na"}]
    return payload


def test_block_reorder_pipeline__accepts_structural_pascal_assembled_from_blocks() -> None:
    payload = {
        "language": "pascal",
        "blocks": ["program Main;", "begin", "writeln('Hello');", "end."],
        "blocks_by_language": {
            "pascal": ["program Main;", "begin", "writeln('Hello');", "end."],
        },
        "correct_order": [0, 1, 2, 3],
        "expected_code": "program Main;\nbegin\n  writeln('Hello');\nend.",
    }
    pipeline = BlockReorderPipeline(_FakeCodeRunner(results=[]))

    result = pipeline.run(
        language_id="pascal",
        code="program Main;\nbegin\nwriteln('Hello');\nend.",
        task_payload=payload,
        block_order=[0, 1, 2, 3],
    )

    assert result["success"] is True
    assert result["semantic_checked"] is False


def test_block_reorder_pipeline__structural_success_without_tests() -> None:
    pipeline = BlockReorderPipeline(_FakeCodeRunner(results=[]))

    result = pipeline.run(
        language_id="python",
        code="print('b')\nprint('a')",
        task_payload=_task_payload(),
        block_order=[1, 0],
    )

    assert result["success"] is True
    assert result["semantic_checked"] is False
    assert result["test_results"] == []


def test_block_reorder_pipeline__structural_failure_skips_semantic() -> None:
    runner = _FakeCodeRunner(
        results=[CaseRunResult(case=1, status="PASSED", inputs="", expected="", actual="", message="")]
    )
    pipeline = BlockReorderPipeline(runner)

    result = pipeline.run(
        language_id="python",
        code="print('a')\nprint('b')",
        task_payload=_task_payload(with_tests=True),
        block_order=[0, 1],
    )

    assert result["success"] is False
    assert result["semantic_checked"] is False
    assert result["test_results"] == []


def test_block_reorder_pipeline__runs_tests_after_structural_success() -> None:
    pipeline = BlockReorderPipeline(
        _FakeCodeRunner(
            results=[
                CaseRunResult(
                    case=1,
                    status="PASSED",
                    inputs="",
                    expected="b\na",
                    actual="b\na",
                    message="",
                )
            ]
        )
    )

    result = pipeline.run(
        language_id="python",
        code="print('b')\nprint('a')",
        task_payload=_task_payload(with_tests=True),
        block_order=[1, 0],
    )

    assert result["success"] is True
    assert result["semantic_checked"] is True
    assert result["test_results"][0]["status"] == "PASSED"


def test_block_reorder_pipeline__semantic_failure_returns_error() -> None:
    pipeline = BlockReorderPipeline(
        _FakeCodeRunner(
            results=[
                CaseRunResult(
                    case=1,
                    status="FAILED",
                    inputs="",
                    expected="b\na",
                    actual="wrong",
                    message="Неверный вывод программы.",
                )
            ]
        )
    )

    result = pipeline.run(
        language_id="python",
        code="print('b')\nprint('a')",
        task_payload=_task_payload(with_tests=True),
        block_order=[1, 0],
    )

    assert result["success"] is False
    assert result["semantic_checked"] is True
    assert result["compiler_errors"][0]["type"] == "SEMANTIC"
