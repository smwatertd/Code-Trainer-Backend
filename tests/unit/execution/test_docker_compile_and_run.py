from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

from src.features.languages.domain.language_config import (
    DockerConfig,
    ExecutionTestConfig,
    LanguageConfig,
    LanguageFeature,
)
from src.shared.execution.checking.docker_code_runner import DockerCodeRunner
from src.shared.execution.checking.docker_executor import DockerRunResult


def test_docker_code_runner__compile_and_run_parses_markers() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="cpp",
        label="C++",
        file_extension=".cpp",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(
            image="cpp_runner",
            compile="g++ {source} -o {binary}",
        ),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            compile=("g++", "{source}", "-o", "{binary}"),
            timeout_seconds=5,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_raw_shell.return_value = DockerRunResult(
        stdout=("__CT_CASE_0_START__\n" "0\n1\n2\n" "__CT_CASE_0_END__\n"),
        stderr="",
        returncode=0,
        duration_ms=12,
        workspace_id="abcd1234",
    )

    runner = DockerCodeRunner(registry, docker=docker)
    results = runner.run_tests(
        "cpp",
        "int main(){return 0;}",
        [{"inputs": "", "output": "0\n1\n2"}],
    )

    assert len(results) == 1
    assert results[0].status == "PASSED"
    docker.run_raw_shell.assert_called_once()
    assert "__CT_CASE_0_START__" in docker.run_raw_shell.call_args[0][1]


def test_docker_code_runner__compile_and_run_reports_compile_failure() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="cpp",
        label="C++",
        file_extension=".cpp",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="cpp_runner", compile="g++ {source} -o {binary}"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            compile=("g++", "{source}", "-o", "{binary}"),
            timeout_seconds=5,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_raw_shell.return_value = DockerRunResult(
        stdout="",
        stderr="/tmp/home/abc/source.cpp:1:1: error: expected ';' before '}' token",
        returncode=1,
        duration_ms=7,
        workspace_id="abcd1234",
    )

    results = DockerCodeRunner(registry, docker=docker).run_tests(
        "cpp",
        "int main(){",
        [{"inputs": "", "output": "0"}],
    )

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert "error:" in results[0].message


def test_docker_code_runner__compile_and_run_reports_missing_markers() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="cpp",
        label="C++",
        file_extension=".cpp",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="cpp_runner", compile="g++ {source} -o {binary}"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            compile=("g++", "{source}", "-o", "{binary}"),
            timeout_seconds=5,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_raw_shell.return_value = DockerRunResult(
        stdout="42\n",
        stderr="",
        returncode=0,
        duration_ms=5,
        workspace_id="abcd1234",
    )

    results = DockerCodeRunner(registry, docker=docker).run_tests(
        "cpp",
        "int main(){return 0;}",
        [{"inputs": "", "output": "42"}],
    )

    assert results[0].status == "ERROR"
    assert results[0].message == "Не удалось прочитать результат выполнения теста."


def test_docker_code_runner__compile_check_reports_timeout_as_compiler_error() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="csharp",
        label="C#",
        file_extension=".cs",
        supported_features=frozenset({LanguageFeature.COMPILE}),
        docker=DockerConfig(image="csharp_runner", compile="dotnet build"),
        test=ExecutionTestConfig(strategy="compile_and_run", timeout_seconds=8),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_diagnostics.side_effect = subprocess.TimeoutExpired(cmd=["docker"], timeout=8)

    errors = DockerCodeRunner(registry, docker=docker).compile_check("csharp", "class Program {}")

    assert errors == ["Превышен лимит времени выполнения (8 с)."]


def test_docker_code_runner__compile_check_falls_back_to_local_without_docker() -> None:
    registry = MagicMock()
    docker = MagicMock()
    docker.is_available.return_value = False

    runner = DockerCodeRunner(registry, docker=docker)
    runner._local_fallback.compile_check = MagicMock(return_value=["local compile error"])

    errors = runner.compile_check("java", "broken")

    assert errors == ["local compile error"]
    runner._local_fallback.compile_check.assert_called_once_with("java", "broken")
