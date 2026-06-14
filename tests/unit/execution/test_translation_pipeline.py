from __future__ import annotations

from pathlib import Path

import pytest

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.code_runner_factory import create_code_runner
from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.pipeline.translation_pipeline import TranslationPipeline
from src.shared.execution.services.guest_job_processor import GuestJobProcessor

_LANGUAGES_DIR = Path(__file__).resolve().parents[3] / "languages"


@pytest.fixture
def translation_pipeline() -> TranslationPipeline:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    return TranslationPipeline(create_code_runner(registry, prefer_docker=False))


def test_translation_pipeline__full_without_tests_fails_even_when_code_compiles(
    translation_pipeline: TranslationPipeline,
) -> None:
    result = translation_pipeline.run(
        language_id="python",
        code="print('Hello')\n",
        task_type="translation",
        task_payload={"source_language": "python", "target_language": "python"},
    )

    assert result["success"] is False
    assert result["test_results"] == []


def test_translation_pipeline__hello_task_passes_with_test_cases(translation_pipeline: TranslationPipeline) -> None:
    result = translation_pipeline.run(
        language_id="python",
        code="print('Hello')\n",
        task_type="translation",
        task_payload={
            "source_language": "python",
            "test_cases": [{"inputs": "", "output": "Hello"}],
        },
    )

    assert result["success"] is True
    assert result["test_results"][0]["status"] == "PASSED"


def test_translation_pipeline__compile_only_failure(translation_pipeline: TranslationPipeline) -> None:
    result = translation_pipeline.run(
        language_id="python",
        code="print('Hello'\n",
        task_type="translation",
        task_payload={},
    )

    assert result["success"] is False
    assert result["compiler_errors"]


def test_translation_pipeline__pattern_check_fails_without_loop(translation_pipeline: TranslationPipeline) -> None:
    result = translation_pipeline.run(
        language_id="python",
        code="print(0)\nprint(1)\n",
        task_type="translation",
        task_payload={"constructions": ["for_loop"]},
        mode="full",
    )

    assert result["success"] is False
    assert result["pattern_errors"]


def test_translation_pipeline__runs_test_cases(translation_pipeline: TranslationPipeline) -> None:
    result = translation_pipeline.run(
        language_id="python",
        code="print(input())\n",
        task_type="translation",
        task_payload={
            "test_cases": [
                {"inputs": "hello", "output": "hello"},
            ],
        },
    )

    assert result["success"] is True
    assert result["test_results"][0]["status"] == "PASSED"


def test_translation_pipeline__wrong_language_code_fails_compile_before_tests(
    translation_pipeline: TranslationPipeline,
) -> None:
    result = translation_pipeline.run(
        language_id="cpp",
        code="print('Hello')\n",
        task_type="translation",
        task_payload={
            "source_language": "python",
            "test_cases": [{"inputs": "", "output": "Hello"}],
        },
    )

    assert result["success"] is False
    assert result["compiler_errors"]
    assert result["test_results"] == []


def test_guest_job_processor__translation_success(translation_pipeline: TranslationPipeline) -> None:
    processor = GuestJobProcessor(translation_pipeline=translation_pipeline)
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print('Hello')\n",
        op="guest_full_check",
        task_id=1,
        payload={
            "task_snapshot": {
                "task_type": "translation",
                "payload": {
                    "source_language": "python",
                    "test_cases": [{"inputs": "", "output": "Hello"}],
                },
            },
        },
    )

    output = processor.process(job)

    assert output["success"] is True
