from __future__ import annotations

from pathlib import Path

import pytest

from src.features.languages.paths import RUFF_STUDENT_CONFIG
from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.local_code_runner import LocalCodeRunner

_LANGUAGES_DIR = Path(__file__).resolve().parents[3] / "languages"


@pytest.fixture
def local_runner() -> LocalCodeRunner:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    return LocalCodeRunner(registry)


def test_python_lint_uses_student_ruff_config() -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    python = registry.get_or_raise("python")

    assert python.local_lint is not None
    assert "--config" in python.local_lint.command
    assert "{ruff_config}" in python.local_lint.command
    assert RUFF_STUDENT_CONFIG.is_file()


def test_python_lint_ignores_trailing_newline(local_runner: LocalCodeRunner) -> None:
    code = 'print("hello")'  # двойные кавычки, без пустой строки в конце
    errors = local_runner.lint("python", code)
    combined = "\n".join(errors).lower()

    assert "newline" not in combined
    assert "w292" not in combined


def test_python_lint_recommends_double_quotes(local_runner: LocalCodeRunner) -> None:
    code = "print('hello')\n"
    errors = local_runner.lint("python", code)
    combined = "\n".join(errors).lower()

    assert "q000" in combined or "double quotes" in combined or "quotes" in combined


def test_python_lint_still_reports_syntax_errors(local_runner: LocalCodeRunner) -> None:
    code = "print('hello'"
    errors = local_runner.lint("python", code)

    assert errors
