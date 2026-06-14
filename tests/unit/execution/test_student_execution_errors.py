from __future__ import annotations

from src.shared.execution.checking.student_execution_errors import (
    GENERIC_COMPILE_FAILED,
    filter_student_compiler_lines,
    is_infrastructure_error,
    redact_infrastructure_error,
)


def test_is_infrastructure_error__detects_docker_messages() -> None:
    assert is_infrastructure_error("Docker command failed with exit code 1")
    assert is_infrastructure_error("Command '['/usr/bin/docker', 'exec']' timed out after 8 seconds")


def test_redact_infrastructure_error__replaces_leaks_with_generic_message() -> None:
    assert redact_infrastructure_error("Docker command failed with exit code 1") == GENERIC_COMPILE_FAILED


def test_redact_infrastructure_error__keeps_compiler_diagnostics() -> None:
    message = "Program.cs(3,1): error CS7021: Cannot declare namespace in script code"
    assert redact_infrastructure_error(message) == message


def test_filter_student_compiler_lines__drops_infrastructure_only_output() -> None:
    assert filter_student_compiler_lines(["Docker command failed with exit code 1"]) == []


def test_filter_student_compiler_lines__drops_fpc_noise() -> None:
    lines = filter_student_compiler_lines(
        [
            "Free Pascal Compiler version 3.2.2 for aarch64",
            "Copyright (c) 1993-2021 by Florian Klaempfl and others",
            'source.pas(1,26) Error: Identifier not found "x"',
            "source.pas(1,33) Fatal: There were 1 errors compiling module, stopping",
            "Fatal: Compilation aborted",
            "Error: /usr/bin/ppca64 returned an error exitcode",
        ]
    )
    assert lines == ['source.pas(1,26) Error: Identifier not found "x"']
