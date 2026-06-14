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


def test_docker_code_runner__docker_one_shot_runs_java_tests() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="java",
        label="Java",
        file_extension=".java",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="java_runner"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            docker_one_shot=(
                "bash -c 'cp {source} /tmp/home/Main.java && "
                "javac -d /tmp/home /tmp/home/Main.java 2>&1 && "
                "java -cp /tmp/home Main'"
            ),
            timeout_seconds=5,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_shell.return_value = DockerRunResult(
        stdout="Hello, World!\n",
        stderr="",
        returncode=0,
        duration_ms=8,
    )

    runner = DockerCodeRunner(registry, docker=docker)
    results = runner.run_tests(
        "java",
        'public class Main { public static void main(String[] args) { System.out.println("x"); } }',
        [{"inputs": "", "output": "Hello, World!"}],
    )

    assert len(results) == 1
    assert results[0].status == "PASSED"
    docker.run_shell.assert_called_once()


def test_docker_code_runner__docker_one_shot_fails_on_wrong_output() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="java",
        label="Java",
        file_extension=".java",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="java_runner"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            docker_one_shot="java Main",
            timeout_seconds=5,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_shell.return_value = DockerRunResult(
        stdout="wrong\n",
        stderr="",
        returncode=0,
        duration_ms=4,
    )

    results = DockerCodeRunner(registry, docker=docker).run_tests(
        "java",
        "public class Main {}",
        [{"inputs": "", "output": "expected"}],
    )

    assert results[0].status == "FAILED"
    assert results[0].message == "Неверный вывод программы."


def test_docker_code_runner__docker_one_shot_reports_runtime_error() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="csharp",
        label="C#",
        file_extension=".csx",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="csharp_runner"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            docker_one_shot="dotnet-script {filename}",
            timeout_seconds=8,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_shell.return_value = DockerRunResult(
        stdout="",
        stderr="dotnet-script: command not found",
        returncode=127,
        duration_ms=2,
    )

    results = DockerCodeRunner(registry, docker=docker).run_tests(
        "csharp",
        'Console.WriteLine("x");',
        [{"inputs": "", "output": "x"}],
    )

    assert results[0].status == "ERROR"
    assert "command not found" in results[0].message


def test_docker_code_runner__docker_one_shot_reports_timeout() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="java",
        label="Java",
        file_extension=".java",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="java_runner"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            docker_one_shot="sleep 10",
            timeout_seconds=5,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_shell.side_effect = subprocess.TimeoutExpired(cmd=["sleep"], timeout=5)

    results = DockerCodeRunner(registry, docker=docker).run_tests(
        "java",
        "public class Main {}",
        [{"inputs": "", "output": "x"}],
    )

    assert results[0].status == "ERROR"
    assert "Превышен лимит времени" in results[0].message


def test_docker_code_runner__falls_back_to_local_when_docker_unavailable() -> None:
    from src.shared.execution.checking.dto import TestCaseResult

    registry = MagicMock()
    local_results = [
        TestCaseResult(case=1, status="PASSED", inputs="", expected="x", actual="x"),
    ]
    docker = MagicMock()
    docker.is_available.return_value = False

    runner = DockerCodeRunner(registry, docker=docker)
    runner._local_fallback.run_tests = MagicMock(return_value=local_results)

    results = runner.run_tests("java", "code", [{"inputs": "", "output": "x"}])

    assert results == local_results
    runner._local_fallback.run_tests.assert_called_once_with("java", "code", [{"inputs": "", "output": "x"}])


def test_docker_code_runner__docker_one_shot_runs_csharp_tests() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="csharp",
        label="C#",
        file_extension=".cs",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="csharp_runner"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            docker_one_shot="DOTNET_NOLOGO=1 dotnet run --no-build {filename}",
            timeout_seconds=30,
        ),
    )
    docker = MagicMock()
    docker.is_available.return_value = True
    docker.run_shell.return_value = DockerRunResult(
        stdout="Hello, World!\n",
        stderr="",
        returncode=0,
        duration_ms=12,
    )

    runner = DockerCodeRunner(registry, docker=docker)
    results = runner.run_tests(
        "csharp",
        'Console.WriteLine("Hello, World!");',
        [{"inputs": "", "output": "Hello, World!"}],
    )

    assert len(results) == 1
    assert results[0].status == "PASSED"
    docker.run_shell.assert_called_once()
