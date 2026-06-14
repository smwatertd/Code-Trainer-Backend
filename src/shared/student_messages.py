from __future__ import annotations

import re

GENERIC_COMPILE_FAILED = "Не удалось скомпилировать программу."
GENERIC_EXECUTION_FAILED = "Не удалось выполнить проверку."
INCORRECT_OUTPUT = "Неверный вывод программы."
COMPILATION_FAILED = "Ошибка компиляции."
TIME_LIMIT_EXCEEDED = "Превышен лимит времени выполнения."
BLOCKS_WRONG_ORDER = "Блоки расставлены в неверном порядке."
BLOCK_ORDER_EMPTY = "Укажите порядок блоков."
BLOCK_INDEX_NEGATIVE = "Индексы блоков не могут быть отрицательными."
BLOCK_ORDER_LENGTH_MISMATCH = "Число блоков не совпадает с заданием."
BLOCK_INDEX_OUT_OF_RANGE = "Индекс блока выходит за пределы списка."
ASSEMBLED_CODE_REQUIRED = "Соберите программу из блоков."
ASSEMBLED_CODE_MISMATCH = "Собранный код не совпадает с выбранным порядком блоков."
SEMANTIC_TEST_FAILED = "Программа не прошла проверку на тестах."
COMPILED_BINARY_MISSING = "Исполняемый файл не был создан после компиляции."
TEST_MARKERS_NOT_FOUND = "Не удалось прочитать результат выполнения теста."


def format_time_limit_exceeded(timeout: int | float) -> str:
    return f"Превышен лимит времени выполнения ({timeout} с)."


_INFRASTRUCTURE_PATTERNS = (
    re.compile(r"^Docker command failed\b", re.IGNORECASE),
    re.compile(r"^Command failed with exit code\b", re.IGNORECASE),
    re.compile(r"docker is not available", re.IGNORECASE),
    re.compile(r"^Command '\[", re.IGNORECASE),
    re.compile(r"timed out after \d+ seconds?", re.IGNORECASE),
    re.compile(r"/usr/bin/docker"),
    re.compile(r"CT_WORKSPACE"),
    re.compile(r"base64 -d"),
    re.compile(r"runner_\w+"),
)

_FPC_NOISE_PATTERNS = (
    re.compile(r"^Free Pascal Compiler version\b", re.IGNORECASE),
    re.compile(r"^Copyright \(c\)", re.IGNORECASE),
    re.compile(r"^Fatal: Compilation aborted\b", re.IGNORECASE),
    re.compile(r"^Fatal: There were \d+ errors compiling module\b", re.IGNORECASE),
    re.compile(r"\.pas\(\d+(?:,\d+)?\)\s*Fatal: There were \d+ errors compiling module\b", re.IGNORECASE),
    re.compile(r"^Error: /usr/bin/\w+ returned an error exitcode\b", re.IGNORECASE),
)


def _is_fpc_noise(message: str) -> bool:
    text = message.strip()
    if not text:
        return True
    return any(pattern.search(text) for pattern in _FPC_NOISE_PATTERNS)


def is_infrastructure_error(message: str) -> bool:
    text = message.strip()
    if not text:
        return False
    return any(pattern.search(text) for pattern in _INFRASTRUCTURE_PATTERNS)


def redact_infrastructure_error(message: str, *, default: str = GENERIC_COMPILE_FAILED) -> str:
    text = message.strip()
    if not text or is_infrastructure_error(text):
        return default
    return text


def filter_student_compiler_lines(lines: list[str]) -> list[str]:
    filtered = [
        line for line in lines if line.strip() and not is_infrastructure_error(line) and not _is_fpc_noise(line)
    ]
    return filtered
