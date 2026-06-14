from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.local_code_runner import LocalCodeRunner, _format_command
from tests.helpers.toolchain import require_fpc

_LANGUAGES_DIR = Path(__file__).resolve().parents[3] / "languages"


@pytest.fixture
def local_runner() -> LocalCodeRunner:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    return LocalCodeRunner(registry)


def test_local_compile_check__pascal_passes(local_runner: LocalCodeRunner) -> None:
    require_fpc()
    code = "program T;\nbegin\n  writeln('ok');\nend.\n"
    errors = local_runner.compile_check("pascal", code)
    assert errors == []


def test_local_compile_check__pascal_reports_missing_fpc(local_runner: LocalCodeRunner) -> None:
    with patch("src.shared.execution.checking.local_code_runner.which", return_value=None):
        errors = local_runner.compile_check("pascal", "program T;\nbegin\n  writeln('ok');\nend.\n")

    assert len(errors) == 1
    assert "fpc" in errors[0]
    assert "не установлен на сервере" in errors[0]


def test_local_run_tests__pascal_reports_missing_fpc(local_runner: LocalCodeRunner) -> None:
    with patch("src.shared.execution.checking.local_code_runner.which", return_value=None):
        results = local_runner.run_tests(
            "pascal",
            "program T;\nbegin\n  writeln('ok');\nend.\n",
            [{"inputs": "", "output": "ok"}],
        )

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert "fpc" in results[0].message
    assert "не установлен на сервере" in results[0].message


def test_language_configs__have_local_compile_for_compiled_languages() -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)

    for language_id in ("pascal", "java", "csharp", "cpp"):
        config = registry.get_or_raise(language_id)
        assert config.local_compile is not None
        assert config.local_compile.command


def test_compiled_language_configs__have_test_execution_strategy() -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)

    for language_id in ("pascal", "java", "csharp", "cpp"):
        config = registry.get_or_raise(language_id)
        assert config.test.strategy == "compile_and_run"
        has_runner = bool(config.test.compile or config.test.local_one_shot or config.test.docker_one_shot)
        assert has_runner, f"{language_id} has no test runner configured"


def test_java_compile_command__uses_detected_class_name() -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    java = registry.get_or_raise("java")
    assert java.local_compile is not None

    command = _format_command(
        java.local_compile.command,
        filename=Path("/tmp/solution.java"),
        output=Path("/tmp/solution.bin"),
    )

    joined = " ".join(command)
    assert "sed" in joined
    assert "${class:-Main}" in joined
    assert "${class}.java" in joined


def test_local_compile_check__java_uses_public_class_name(local_runner: LocalCodeRunner) -> None:
    if shutil.which("javac") is None:
        pytest.fail("javac is not installed")
    try:
        subprocess.run(["javac", "-version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        pytest.fail(f"javac is not available: {exc}")

    code = (
        "public class HelloWorld {\n"
        "    public static void main(String[] args) {\n"
        '        System.out.println("Hello");\n'
        "    }\n"
        "}\n"
    )
    errors = local_runner.compile_check("java", code)
    if any("Java Runtime" in err or "Unable to locate" in err for err in errors):
        pytest.fail(f"javac is not available: {errors}")
    assert errors == []


def test_pascal_test_compile__uses_glued_output_flag() -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(_LANGUAGES_DIR)
    pascal = registry.get_or_raise("pascal")

    assert pascal.test.compile is not None
    assert "-o{binary}" in pascal.test.compile
