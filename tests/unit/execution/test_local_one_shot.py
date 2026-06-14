from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.features.languages.domain.language_config import (
    DockerConfig,
    ExecutionTestConfig,
    LanguageConfig,
    LanguageFeature,
)
from src.shared.execution.checking.local_code_runner import LocalCodeRunner


def _java_config(*, local_one_shot: str | None = None, docker_one_shot: str | None = None) -> LanguageConfig:
    return LanguageConfig(
        id="java",
        label="Java",
        file_extension=".java",
        supported_features=frozenset({LanguageFeature.TEST}),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            local_one_shot=local_one_shot,
            docker_one_shot=docker_one_shot,
            timeout_seconds=5,
        ),
    )


def _completed(stdout: str = "", stderr: str = "", *, returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_local_code_runner__local_one_shot_passes() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = _java_config(
        local_one_shot=(
            'workdir="$(dirname "{source}")" && cp "{source}" "$workdir/Main.java" && '
            'javac -d "$workdir" "$workdir/Main.java" && java -cp "$workdir" Main'
        ),
    )

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        return_value=_completed("Hello, World!\n"),
    ) as run_subprocess:
        results = LocalCodeRunner(registry).run_tests(
            "java",
            'public class Main { public static void main(String[] args) { System.out.println("x"); } }',
            [{"inputs": "", "output": "Hello, World!"}],
        )

    assert len(results) == 1
    assert results[0].status == "PASSED"
    run_subprocess.assert_called_once()
    command = run_subprocess.call_args[0][0]
    assert command[0] == "bash"
    assert command[1] == "-lc"
    assert "Main.java" in command[2]


def test_local_code_runner__local_one_shot_fails_on_wrong_output() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = _java_config(local_one_shot='echo "{source}"')

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        return_value=_completed("wrong\n"),
    ):
        results = LocalCodeRunner(registry).run_tests(
            "java",
            "public class Main {}",
            [{"inputs": "", "output": "expected"}],
        )

    assert results[0].status == "FAILED"
    assert results[0].message == "Неверный вывод программы."
    assert results[0].actual == "wrong"


def test_local_code_runner__local_one_shot_reports_compile_error() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = _java_config(local_one_shot="javac {source}")

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        return_value=_completed(stderr="error: cannot find symbol", returncode=1),
    ):
        results = LocalCodeRunner(registry).run_tests(
            "java",
            "public class Main {}",
            [{"inputs": "", "output": "x"}],
        )

    assert results[0].status == "ERROR"
    assert "cannot find symbol" in results[0].message


def test_local_code_runner__local_one_shot_reports_timeout() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = _java_config(local_one_shot="sleep 10")

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        side_effect=subprocess.TimeoutExpired(cmd=["sleep"], timeout=5),
    ):
        results = LocalCodeRunner(registry).run_tests(
            "java",
            "public class Main {}",
            [{"inputs": "", "output": "x"}],
        )

    assert results[0].status == "ERROR"
    assert "Превышен лимит времени" in results[0].message


def test_local_code_runner__prefers_local_one_shot_over_docker_one_shot() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = _java_config(
        local_one_shot="echo local",
        docker_one_shot="echo docker",
    )

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        return_value=_completed("local\n"),
    ) as run_subprocess:
        results = LocalCodeRunner(registry).run_tests(
            "java",
            "public class Main {}",
            [{"inputs": "", "output": "local"}],
        )

    assert results[0].status == "PASSED"
    assert "local" in run_subprocess.call_args[0][0][2]
    assert "docker" not in run_subprocess.call_args[0][0][2]


def test_local_code_runner__uses_docker_one_shot_when_local_missing() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="csharp",
        label="C#",
        file_extension=".cs",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(image="csharp_runner"),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            docker_one_shot="DOTNET_NOLOGO=1 dotnet run --no-build",
            timeout_seconds=30,
        ),
    )

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        return_value=_completed("Hello, World!\n"),
    ) as run_subprocess:
        results = LocalCodeRunner(registry).run_tests(
            "csharp",
            'Console.WriteLine("Hello, World!");',
            [{"inputs": "", "output": "Hello, World!"}],
        )

    assert results[0].status == "PASSED"
    assert "dotnet run" in run_subprocess.call_args[0][0][2]


def test_local_code_runner__compile_and_run_used_when_test_compile_configured() -> None:
    registry = MagicMock()
    registry.get_or_raise.return_value = LanguageConfig(
        id="pascal",
        label="Pascal",
        file_extension=".pas",
        supported_features=frozenset({LanguageFeature.TEST}),
        test=ExecutionTestConfig(
            strategy="compile_and_run",
            compile=("fpc", "{source}", "-o{binary}"),
            docker_one_shot="ignored",
            timeout_seconds=3,
        ),
    )

    with patch(
        "src.shared.execution.checking.local_code_runner._run_subprocess",
        side_effect=lambda command, **kwargs: _prepare_pascal_compile(command),
    ) as run_subprocess:
        results = LocalCodeRunner(registry).run_tests(
            "pascal",
            "program T; begin end.",
            [{"inputs": "", "output": "1\n2\n3"}],
        )

    assert results[0].status == "PASSED"
    assert run_subprocess.call_count == 2
    compile_command = run_subprocess.call_args_list[0][0][0]
    assert compile_command[0] == "fpc"


def _prepare_pascal_compile(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    if command and command[0] == "fpc":
        for part in command:
            if part.startswith("-o"):
                binary = Path(part[2:])
                binary.write_text("#!/bin/sh\necho 1\necho 2\necho 3\n", encoding="utf-8")
                binary.chmod(0o755)
        return _completed()
    return _completed("1\n2\n3\n")
