from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path
from shutil import which
from typing import Any

from src.features.languages.domain.language_config import LanguageConfig, LanguageFeature
from src.features.languages.paths import RUFF_STUDENT_CONFIG
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.dto import TestCaseResult
from src.shared.execution.checking.student_execution_errors import (
    COMPILATION_FAILED,
    COMPILED_BINARY_MISSING,
    GENERIC_COMPILE_FAILED,
    INCORRECT_OUTPUT,
    filter_student_compiler_lines,
    format_time_limit_exceeded,
    redact_infrastructure_error,
)


def _case_inputs(test_case: dict[str, Any]) -> str:
    raw = test_case.get("inputs", test_case.get("input", ""))
    return "" if raw is None else str(raw)


def _case_output(test_case: dict[str, Any]) -> str:
    raw = test_case.get("output", test_case.get("expected_output", test_case.get("expected", "")))
    return "" if raw is None else str(raw)


def _truncate(text: str, max_len: int = 300) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text


_SYSTEM_WRAPPERS = frozenset({"bash", "sh", "python", "python3"})


def _missing_toolchain_message(executable: str) -> str:
    return f"Компилятор '{executable}' не установлен на сервере"


def _ensure_toolchain_available(command: list[str]) -> None:
    if not command:
        return
    executable = command[0]
    if executable in _SYSTEM_WRAPPERS:
        return
    if which(executable) is None:
        raise FileNotFoundError(_missing_toolchain_message(executable))


def _format_command(template: tuple[str, ...] | str, *, filename: Path, output: Path) -> list[str]:
    mapping = {
        "filename": str(filename),
        "source": str(filename),
        "binary": str(output),
        "output": str(output),
        "ruff_config": str(RUFF_STUDENT_CONFIG),
    }
    if isinstance(template, str):
        return [template.format(**mapping)]
    return [part.format(**mapping) for part in template]


def _run_subprocess(command: list[str], *, stdin: str | None = None, timeout: int) -> subprocess.CompletedProcess[str]:
    _ensure_toolchain_available(command)
    return subprocess.run(
        command,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _diagnostics_from_process(result: subprocess.CompletedProcess[str]) -> list[str]:
    if result.returncode == 0:
        return []
    combined = f"{result.stderr}\n{result.stdout}".strip()
    lines = filter_student_compiler_lines([line.strip() for line in combined.splitlines() if line.strip()])
    return lines or [GENERIC_COMPILE_FAILED]


def _wrap_stdin_lines(code: str, stdin_data: str) -> str:
    lines = stdin_data.splitlines()
    setup = "\n".join(f"data.append({line!r})" for line in lines)
    return (
        "import sys\n"
        "data = []\n"
        f"{setup}\n"
        "it = iter(data)\n"
        "def input(prompt=''):\n"
        "    try:\n"
        "        return next(it)\n"
        "    except StopIteration:\n"
        "        return ''\n"
        f"{code}"
    )


class LocalCodeRunner:
    def __init__(self, registry: LanguageRegistry, *, default_timeout_seconds: int = 5) -> None:
        self._registry = registry
        self._default_timeout_seconds = default_timeout_seconds

    def compile_check(self, language_id: str, code: str) -> list[str]:
        cfg = self._registry.get_or_raise(language_id)
        if not cfg.supports(LanguageFeature.COMPILE):
            return []
        command = cfg.local_compile.command if cfg.local_compile else None
        if not command:
            return [f"Local compile is not configured for language '{cfg.id}'"]
        return self._run_with_temp_file(cfg, code, command)

    def lint(self, language_id: str, code: str) -> list[str]:
        cfg = self._registry.get_or_raise(language_id)
        if not cfg.supports(LanguageFeature.LINT):
            return []
        command = cfg.local_lint.command if cfg.local_lint else None
        if not command:
            return []
        return self._run_with_temp_file(cfg, code, command)

    def run_tests(self, language_id: str, code: str, test_cases: list[dict[str, Any]]) -> list[TestCaseResult]:
        cfg = self._registry.get_or_raise(language_id)
        if not test_cases:
            return []
        if not cfg.supports(LanguageFeature.TEST):
            return self._unsupported_tests(test_cases)

        strategy = cfg.test.strategy
        if strategy == "stdin_lines":
            return self._run_stdin_lines(cfg, code, test_cases)
        if strategy == "compile_and_run":
            if (cfg.test.local_one_shot or cfg.test.docker_one_shot) and not cfg.test.compile:
                return self._run_local_one_shot(cfg, code, test_cases)
            return self._run_compile_and_run(cfg, code, test_cases)
        return self._unsupported_tests(test_cases)

    def _unsupported_tests(self, test_cases: list[dict[str, Any]]) -> list[TestCaseResult]:
        return [
            TestCaseResult(
                case=index + 1,
                status="ERROR",
                inputs=_case_inputs(test_case),
                expected=_case_output(test_case).strip(),
                actual="",
                message="Test strategy is not supported in local runner",
            )
            for index, test_case in enumerate(test_cases)
        ]

    def _run_local_one_shot(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> list[TestCaseResult]:
        template = cfg.test.local_one_shot or cfg.test.docker_one_shot
        if not template:
            return self._unsupported_tests(test_cases)

        timeout = cfg.test.timeout_seconds or self._default_timeout_seconds
        results: list[TestCaseResult] = []

        try:
            with tempfile.TemporaryDirectory(prefix="ct-local-") as tmp:
                source = Path(tmp) / f"solution{cfg.file_extension}"
                binary = Path(tmp) / "solution.bin"
                source.write_text(code, encoding="utf-8")
                command = _format_command(
                    ("bash", "-lc", template),
                    filename=source,
                    output=binary,
                )

                for index, test_case in enumerate(test_cases):
                    inputs_str = _case_inputs(test_case)
                    expected = _case_output(test_case).strip()
                    started = time.perf_counter()
                    try:
                        process = _run_subprocess(command, stdin=inputs_str or None, timeout=timeout)
                        duration_ms = int((time.perf_counter() - started) * 1000)
                        actual = (process.stdout or "").strip()
                        stderr = (process.stderr or "").strip()
                        if process.returncode != 0 and stderr:
                            err_text = _truncate(stderr)
                            results.append(
                                TestCaseResult(
                                    case=index + 1,
                                    status="ERROR",
                                    inputs=inputs_str,
                                    expected=expected,
                                    actual=err_text,
                                    message=err_text,
                                    duration_ms=duration_ms,
                                )
                            )
                        elif actual == expected:
                            results.append(
                                TestCaseResult(
                                    case=index + 1,
                                    status="PASSED",
                                    inputs=inputs_str,
                                    expected=expected,
                                    actual=actual,
                                    duration_ms=duration_ms,
                                )
                            )
                        else:
                            results.append(
                                TestCaseResult(
                                    case=index + 1,
                                    status="FAILED",
                                    inputs=inputs_str,
                                    expected=expected,
                                    actual=actual or _truncate(stderr),
                                    message=INCORRECT_OUTPUT,
                                    duration_ms=duration_ms,
                                )
                            )
                    except subprocess.TimeoutExpired:
                        results.append(
                            TestCaseResult(
                                case=index + 1,
                                status="ERROR",
                                inputs=inputs_str,
                                expected=expected,
                                actual="",
                                message=format_time_limit_exceeded(timeout),
                            )
                        )
        except Exception as exc:
            return [
                TestCaseResult(
                    case=index + 1,
                    status="ERROR",
                    inputs=_case_inputs(test_case),
                    expected=_case_output(test_case).strip(),
                    actual=redact_infrastructure_error(str(exc)),
                    message=redact_infrastructure_error(str(exc)),
                )
                for index, test_case in enumerate(test_cases)
            ]

        return results

    def _run_compile_and_run(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> list[TestCaseResult]:
        compile_template = cfg.test.compile
        if not compile_template:
            return self._unsupported_tests(test_cases)

        timeout = cfg.test.timeout_seconds or self._default_timeout_seconds
        results: list[TestCaseResult] = []

        try:
            with tempfile.TemporaryDirectory(prefix="ct-local-") as tmp:
                source = Path(tmp) / f"solution{cfg.file_extension}"
                binary = Path(tmp) / "solution.bin"
                source.write_text(code, encoding="utf-8")
                compile_command = _format_command(compile_template, filename=source, output=binary)
                compile_process = _run_subprocess(compile_command, timeout=timeout)
                if compile_process.returncode != 0:
                    compile_error = _truncate(f"{compile_process.stderr}\n{compile_process.stdout}".strip())
                    return [
                        TestCaseResult(
                            case=index + 1,
                            status="ERROR",
                            inputs=_case_inputs(test_case),
                            expected=_case_output(test_case).strip(),
                            actual=compile_error,
                            message=compile_error or COMPILATION_FAILED,
                        )
                        for index, test_case in enumerate(test_cases)
                    ]

                run_binary = binary
                if not run_binary.exists():
                    candidates = sorted(Path(tmp).glob("solution*"))
                    run_binary = next(
                        (path for path in candidates if path.is_file() and path != source),
                        binary,
                    )
                if not run_binary.exists():
                    message = COMPILED_BINARY_MISSING
                    return [
                        TestCaseResult(
                            case=index + 1,
                            status="ERROR",
                            inputs=_case_inputs(test_case),
                            expected=_case_output(test_case).strip(),
                            actual=message,
                            message=message,
                        )
                        for index, test_case in enumerate(test_cases)
                    ]

                run_binary.chmod(run_binary.stat().st_mode | 0o111)

                for index, test_case in enumerate(test_cases):
                    inputs_str = _case_inputs(test_case)
                    expected = _case_output(test_case).strip()
                    started = time.perf_counter()
                    try:
                        process = _run_subprocess(
                            [str(run_binary)],
                            stdin=inputs_str or None,
                            timeout=timeout,
                        )
                        duration_ms = int((time.perf_counter() - started) * 1000)
                        actual = (process.stdout or "").strip()
                        stderr = (process.stderr or "").strip()
                        if process.returncode != 0 and stderr:
                            err_text = _truncate(stderr)
                            results.append(
                                TestCaseResult(
                                    case=index + 1,
                                    status="ERROR",
                                    inputs=inputs_str,
                                    expected=expected,
                                    actual=err_text,
                                    message=err_text,
                                    duration_ms=duration_ms,
                                )
                            )
                        elif actual == expected:
                            results.append(
                                TestCaseResult(
                                    case=index + 1,
                                    status="PASSED",
                                    inputs=inputs_str,
                                    expected=expected,
                                    actual=actual,
                                    duration_ms=duration_ms,
                                )
                            )
                        else:
                            results.append(
                                TestCaseResult(
                                    case=index + 1,
                                    status="FAILED",
                                    inputs=inputs_str,
                                    expected=expected,
                                    actual=actual or _truncate(stderr),
                                    message=INCORRECT_OUTPUT,
                                    duration_ms=duration_ms,
                                )
                            )
                    except subprocess.TimeoutExpired:
                        results.append(
                            TestCaseResult(
                                case=index + 1,
                                status="ERROR",
                                inputs=inputs_str,
                                expected=expected,
                                actual="",
                                message=format_time_limit_exceeded(timeout),
                            )
                        )
        except Exception as exc:
            message = redact_infrastructure_error(str(exc))
            return [
                TestCaseResult(
                    case=index + 1,
                    status="ERROR",
                    inputs=_case_inputs(test_case),
                    expected=_case_output(test_case).strip(),
                    actual=message,
                    message=message,
                )
                for index, test_case in enumerate(test_cases)
            ]

        return results

    def _run_stdin_lines(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> list[TestCaseResult]:
        run_command = cfg.test.run
        if not run_command:
            run_command = ("python", "{filename}")

        timeout = cfg.test.timeout_seconds or self._default_timeout_seconds
        results: list[TestCaseResult] = []

        for index, test_case in enumerate(test_cases):
            inputs_str = _case_inputs(test_case)
            expected = _case_output(test_case).strip()
            wrapped = _wrap_stdin_lines(code, inputs_str)
            started = time.perf_counter()
            try:
                with tempfile.TemporaryDirectory(prefix="ct-local-") as tmp:
                    source = Path(tmp) / f"solution{cfg.file_extension}"
                    binary = Path(tmp) / "solution.bin"
                    source.write_text(wrapped, encoding="utf-8")
                    command = _format_command(run_command, filename=source, output=binary)
                    process = _run_subprocess(command, timeout=timeout)
                    duration_ms = int((time.perf_counter() - started) * 1000)
                    actual = (process.stdout or "").strip()
                    stderr = (process.stderr or "").strip()
                    if process.returncode != 0 and stderr:
                        err_text = _truncate(stderr)
                        results.append(
                            TestCaseResult(
                                case=index + 1,
                                status="ERROR",
                                inputs=inputs_str,
                                expected=expected,
                                actual=err_text,
                                message=err_text,
                                duration_ms=duration_ms,
                            )
                        )
                    elif actual == expected:
                        results.append(
                            TestCaseResult(
                                case=index + 1,
                                status="PASSED",
                                inputs=inputs_str,
                                expected=expected,
                                actual=actual,
                                duration_ms=duration_ms,
                            )
                        )
                    else:
                        results.append(
                            TestCaseResult(
                                case=index + 1,
                                status="FAILED",
                                inputs=inputs_str,
                                expected=expected,
                                actual=actual or _truncate(stderr),
                                message=INCORRECT_OUTPUT,
                                duration_ms=duration_ms,
                            )
                        )
            except subprocess.TimeoutExpired:
                results.append(
                    TestCaseResult(
                        case=index + 1,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=format_time_limit_exceeded(timeout),
                    )
                )
            except Exception as exc:
                results.append(
                    TestCaseResult(
                        case=index + 1,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual=redact_infrastructure_error(str(exc)),
                        message=redact_infrastructure_error(str(exc)),
                    )
                )

        return results

    def _run_with_temp_file(
        self,
        cfg: LanguageConfig,
        code: str,
        command_template: tuple[str, ...],
        *,
        timeout_seconds: int | None = None,
    ) -> list[str]:
        timeout = timeout_seconds or self._default_timeout_seconds
        try:
            with tempfile.TemporaryDirectory(prefix="ct-local-") as tmp:
                source = Path(tmp) / f"solution{cfg.file_extension}"
                output = Path(tmp) / "solution.bin"
                source.write_text(code, encoding="utf-8")
                command = _format_command(command_template, filename=source, output=output)
                process = _run_subprocess(command, timeout=timeout)
                return _diagnostics_from_process(process)
        except subprocess.TimeoutExpired:
            return [format_time_limit_exceeded(timeout)]
        except Exception as exc:
            return [redact_infrastructure_error(str(exc))]
