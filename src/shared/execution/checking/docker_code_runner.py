from __future__ import annotations

import base64
import subprocess
from typing import Any

from src.core.settings import ExecutionSettings
from src.features.languages.domain.language_config import LanguageConfig, LanguageFeature
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.docker_executor import DockerExecutor, DockerRunResult
from src.shared.execution.checking.dto import TestCaseResult
from src.shared.execution.checking.execution_workspace import binary_path, source_path
from src.shared.execution.checking.local_code_runner import (
    LocalCodeRunner,
    _case_inputs,
    _case_output,
    _truncate,
    _wrap_stdin_lines,
)
from src.shared.execution.checking.student_execution_errors import (
    COMPILATION_FAILED,
    GENERIC_COMPILE_FAILED,
    INCORRECT_OUTPUT,
    TEST_MARKERS_NOT_FOUND,
    format_time_limit_exceeded,
    redact_infrastructure_error,
)


class DockerCodeRunner:
    def __init__(
        self,
        registry: LanguageRegistry,
        *,
        execution_settings: ExecutionSettings | None = None,
        docker: DockerExecutor | None = None,
    ) -> None:
        self._registry = registry
        self._docker = docker or DockerExecutor(execution_settings)
        self._local_fallback = LocalCodeRunner(registry)

    def is_available(self) -> bool:
        return self._docker.is_available()

    def compile_check(self, language_id: str, code: str) -> list[str]:
        if not self._docker.is_available():
            return self._local_fallback.compile_check(language_id, code)
        return self._run_mode(language_id, code, mode="compile")

    def lint(self, language_id: str, code: str) -> list[str]:
        if not self._docker.is_available():
            return self._local_fallback.lint(language_id, code)
        return self._run_mode(language_id, code, mode="lint")

    def run_tests(self, language_id: str, code: str, test_cases: list[dict[str, Any]]) -> list[TestCaseResult]:
        if not self._docker.is_available():
            return self._local_fallback.run_tests(language_id, code, test_cases)
        cfg = self._registry.get_or_raise(language_id)
        if not test_cases or not cfg.supports(LanguageFeature.TEST):
            return []
        strategy = cfg.test.strategy
        if strategy == "stdin_lines":
            return self._run_stdin_lines(cfg, code, test_cases)
        if strategy == "compile_and_run":
            if cfg.test.docker_one_shot and not cfg.test.compile:
                return self._run_docker_one_shot(cfg, code, test_cases)
            return self._run_compile_and_run(cfg, code, test_cases)
        return self._local_fallback.run_tests(language_id, code, test_cases)

    def _run_mode(self, language_id: str, code: str, *, mode: str) -> list[str]:
        cfg = self._registry.get_or_raise(language_id)
        if not cfg.docker or not cfg.docker.image:
            if mode == "compile":
                return self._local_fallback.compile_check(language_id, code)
            return self._local_fallback.lint(language_id, code)

        if mode == "lint":
            if not cfg.supports(LanguageFeature.LINT) or not cfg.docker.lint:
                return []
            command = cfg.docker.lint
        else:
            if not cfg.supports(LanguageFeature.COMPILE):
                return []
            command = cfg.docker.compile or cfg.docker.run
            if not command:
                return []

        timeout = cfg.test.timeout_seconds or DockerExecutor.DEFAULT_TIMEOUT
        try:
            return self._docker.run_diagnostics(
                cfg.docker.image,
                command,
                code,
                cfg.file_extension,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return [format_time_limit_exceeded(timeout)]
        except Exception as exc:
            return [redact_infrastructure_error(str(exc), default=GENERIC_COMPILE_FAILED)]

    def _run_stdin_lines(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> list[TestCaseResult]:
        if not cfg.docker or not cfg.docker.image:
            return self._local_fallback.run_tests(cfg.id, code, test_cases)

        run_cmd = cfg.docker.run or "python {filename}"
        timeout = cfg.test.timeout_seconds
        results: list[TestCaseResult] = []

        for index, test_case in enumerate(test_cases):
            inputs_str = _case_inputs(test_case)
            expected = _case_output(test_case).strip()
            wrapped = _wrap_stdin_lines(code, inputs_str)
            try:
                result = self._docker.run_shell(
                    cfg.docker.image,
                    run_cmd,
                    wrapped,
                    cfg.file_extension,
                    timeout=timeout,
                )
                results.append(self._map_run_result(index, test_case, result, expected, inputs_str, timeout))
            except subprocess.TimeoutExpired:
                results.append(self._timeout_result(index, test_case, expected, timeout))
            except Exception as exc:
                results.append(self._error_result(index, test_case, expected, redact_infrastructure_error(str(exc))))

        return results

    def _run_docker_one_shot(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> list[TestCaseResult]:
        template = cfg.test.docker_one_shot
        if not template or not cfg.docker or not cfg.docker.image:
            return self._local_fallback.run_tests(cfg.id, code, test_cases)

        timeout = cfg.test.timeout_seconds or DockerExecutor.DEFAULT_TIMEOUT
        results: list[TestCaseResult] = []

        for index, test_case in enumerate(test_cases):
            inputs_str = _case_inputs(test_case)
            expected = _case_output(test_case).strip()
            try:
                result = self._docker.run_shell(
                    cfg.docker.image,
                    template,
                    code,
                    cfg.file_extension,
                    timeout=timeout,
                    stdin=inputs_str or None,
                )
                results.append(self._map_run_result(index, test_case, result, expected, inputs_str, timeout))
            except subprocess.TimeoutExpired:
                results.append(self._timeout_result(index, test_case, expected, timeout))
            except Exception as exc:
                results.append(self._error_result(index, test_case, expected, redact_infrastructure_error(str(exc))))

        return results

    def _run_compile_and_run(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict[str, Any]],
    ) -> list[TestCaseResult]:
        if not cfg.docker or not cfg.docker.image:
            return self._local_fallback.run_tests(cfg.id, code, test_cases)

        compile_template = cfg.test.compile
        if not compile_template:
            return self._local_fallback.run_tests(cfg.id, code, test_cases)

        timeout = cfg.test.timeout_seconds or DockerExecutor.DEFAULT_TIMEOUT
        from src.shared.execution.checking.execution_workspace import new_workspace_id

        workspace_id = new_workspace_id()
        source = source_path(workspace_id, cfg.file_extension)
        binary = binary_path(workspace_id)
        compile_cmd = self._format_compile_command(compile_template, cfg.file_extension, workspace_id)
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

        script_lines = [
            f"echo {code_b64} | base64 -d > {source}",
            compile_cmd,
            f"chmod +x {binary}",
        ]
        for index, test_case in enumerate(test_cases):
            inputs_str = _case_inputs(test_case)
            script_lines.append(f"echo __CT_CASE_{index}_START__")
            if inputs_str:
                input_b64 = base64.b64encode(inputs_str.encode("utf-8")).decode("ascii")
                script_lines.append(f"echo {input_b64} | base64 -d | {binary}")
            else:
                script_lines.append(binary)
            script_lines.append(f"echo __CT_CASE_{index}_END__")

        inner = "\n".join(script_lines)
        try:
            result = self._docker.run_raw_shell(
                cfg.docker.image,
                inner,
                timeout=timeout,
                workspace_id=workspace_id,
            )
        except subprocess.TimeoutExpired:
            return [
                self._timeout_result(index, test_case, _case_output(test_case).strip(), timeout)
                for index, test_case in enumerate(test_cases)
            ]
        except Exception as exc:
            message = redact_infrastructure_error(str(exc))
            return [
                self._error_result(index, test_case, _case_output(test_case).strip(), message)
                for index, test_case in enumerate(test_cases)
            ]

        if result.returncode != 0 and "__CT_CASE_0_START__" not in result.stdout:
            compile_error = _truncate(result.combined_output)
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

        return [
            self._map_parsed_case_result(index, test_case, result.stdout, result.duration_ms)
            for index, test_case in enumerate(test_cases)
        ]

    def _map_parsed_case_result(
        self,
        index: int,
        test_case: dict[str, Any],
        stdout: str,
        duration_ms: int,
    ) -> TestCaseResult:
        inputs_str = _case_inputs(test_case)
        expected = _case_output(test_case).strip()
        start_marker = f"__CT_CASE_{index}_START__"
        end_marker = f"__CT_CASE_{index}_END__"
        start = stdout.find(start_marker)
        end = stdout.find(end_marker)
        if start == -1 or end == -1 or end <= start:
            message = TEST_MARKERS_NOT_FOUND
            return TestCaseResult(
                case=index + 1,
                status="ERROR",
                inputs=inputs_str,
                expected=expected,
                actual=message,
                message=message,
                duration_ms=duration_ms,
            )
        actual = stdout[start + len(start_marker) : end].strip()
        if actual == expected:
            status = "PASSED"
            message = ""
        else:
            status = "FAILED"
            message = INCORRECT_OUTPUT
        return TestCaseResult(
            case=index + 1,
            status=status,
            inputs=inputs_str,
            expected=expected,
            actual=actual,
            message=message,
            duration_ms=duration_ms,
        )

    @staticmethod
    def _format_compile_command(
        compile_template: tuple[str, ...] | str,
        ext: str,
        workspace_id: str,
    ) -> str:
        source = source_path(workspace_id, ext)
        binary = binary_path(workspace_id)
        mapping = {
            "filename": source,
            "source": source,
            "binary": binary,
            "output": binary,
        }
        if isinstance(compile_template, str):
            return compile_template.format(**mapping)
        return " ".join(part.format(**mapping) for part in compile_template)

    def _map_run_result(
        self,
        index: int,
        test_case: dict[str, Any],
        result: DockerRunResult,
        expected: str,
        inputs_str: str,
        timeout: int,
    ) -> TestCaseResult:
        actual = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        if result.returncode != 0 and stderr:
            err_text = _truncate(stderr)
            return TestCaseResult(
                case=index + 1,
                status="ERROR",
                inputs=inputs_str,
                expected=expected,
                actual=err_text,
                message=err_text,
                duration_ms=result.duration_ms,
            )
        if actual == expected:
            return TestCaseResult(
                case=index + 1,
                status="PASSED",
                inputs=inputs_str,
                expected=expected,
                actual=actual,
                duration_ms=result.duration_ms,
            )
        return TestCaseResult(
            case=index + 1,
            status="FAILED",
            inputs=inputs_str,
            expected=expected,
            actual=actual or _truncate(stderr),
            message=INCORRECT_OUTPUT,
            duration_ms=result.duration_ms,
        )

    @staticmethod
    def _timeout_result(
        index: int,
        test_case: dict[str, Any],
        expected: str,
        timeout: int,
    ) -> TestCaseResult:
        inputs_str = _case_inputs(test_case)
        return TestCaseResult(
            case=index + 1,
            status="ERROR",
            inputs=inputs_str,
            expected=expected,
            actual="",
            message=format_time_limit_exceeded(timeout),
        )

    @staticmethod
    def _error_result(
        index: int,
        test_case: dict[str, Any],
        expected: str,
        message: str,
    ) -> TestCaseResult:
        return TestCaseResult(
            case=index + 1,
            status="ERROR",
            inputs=_case_inputs(test_case),
            expected=expected,
            actual=message,
            message=message,
        )
