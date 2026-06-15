from __future__ import annotations

import importlib.util
from pathlib import Path

from migrations.seeds.tc42_course_catalog_generated import build_tc42_course_catalog

_ROOT = Path(__file__).resolve().parents[3]


def _load_block_reorder_module():
    path = _ROOT / "src/features/tasks/domain/block_reorder_language.py"
    spec = importlib.util.spec_from_file_location("block_reorder_language", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load block reorder module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_br = _load_block_reorder_module()
_assemble = _br.assemble_block_reorder_code
_block_reorder_statements = _br.block_reorder_statements
_resolve_block_reorder_correct_order = _br.resolve_block_reorder_correct_order


def _catalog_by_id() -> dict[int, dict]:
    return {row["id"]: row for row in build_tc42_course_catalog()}


def _pascal_example(task_id: int) -> str:
    payload = _catalog_by_id()[task_id]["payload"]
    return str(payload.get("code_examples", {}).get("pascal", ""))


def _block_payload(task_id: int, *, language: str = "pascal") -> dict:
    payload = _catalog_by_id()[task_id]["payload"]
    statements = _block_reorder_statements(payload, language)
    block_order = _resolve_block_reorder_correct_order(payload, language, statements)
    code = _assemble(statements, block_order, language)
    return {
        "task_id": task_id,
        "language": language,
        "code": code,
        "block_order": block_order,
    }


# TC42 task 1 — block: поиск максимума в массиве (Pascal)
TASK1_HELLO_BLOCKS: dict = _block_payload(1)

# TC42 task 5 — block: сумма элементов массива
TASK4_AREA_BLOCKS: dict = _block_payload(5)

# TC42 task 9 — block: максимум из трёх чисел
TASK10_MINUTES_BLOCKS: dict = _block_payload(9)

# TC42 task 3 — translation: поиск минимума
TASK3_SUM_PASCAL: dict = {
    "task_id": 3,
    "language": "pascal",
    "code": _pascal_example(3),
}

# TC42 task 4 — debug: подсчёт положительных чисел
TASK2_AGE_PASCAL: dict = {
    "task_id": 4,
    "language": "pascal",
    "code": _pascal_example(4),
}

TASK2_AGE_BROKEN: dict = {
    "task_id": 4,
    "language": "pascal",
    "code": (
        "var n, i, amount, count: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  count := 1;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(amount);\n"
        "    if amount > 0 then count := count + 1;\n"
        "  end;\n"
        "  writeln(count);\n"
        "end."
    ),
}

# TC42 task 5 — block sum (legacy names kept for existing tests)
TASK5_PERIMETER_OK: dict = dict(TASK4_AREA_BLOCKS)

TASK5_PERIMETER_BROKEN: dict = {
    **TASK4_AREA_BLOCKS,
    "code": (
        "program Solution;\n"
        "begin\n"
        "  var n, i, sale, total: integer;\n"
        "  begin\n"
        "  readln(n);\n"
        "  total := 1;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "  readln(sale);\n"
        "  total := total + sale;\n"
        "  end;\n"
        "  writeln(total);\n"
        "  end.\n"
        "end."
    ),
}

# TC42 task 12 — debug: проверка корректности даты (Python fix)
TASK8_LAST_DIGIT_OK: dict = {
    "task_id": 12,
    "language": "python",
    "code": _catalog_by_id()[12]["payload"]["code_examples"]["python"],
}

TASK8_LAST_DIGIT_BROKEN: dict = {
    "task_id": 12,
    "language": "pascal",
    "code": (
        "var d,m: integer;\n"
        "begin\n"
        "  readln(d,m);\n"
        "  if (m >= 1) and (m <= 12) and (d >= 1) and (d <= 31) then writeln('invalid') else writeln('valid');\n"
        "end."
    ),
}

# TC42 task 11 — translation: тип треугольника
TASK9_DIGIT_SUM_PASCAL: dict = {
    "task_id": 11,
    "language": "pascal",
    "code": _pascal_example(11),
}

TASK12_RECEIPT_PASCAL: dict = {
    "task_id": 16,
    "language": "pascal",
    "code": _pascal_example(16),
}

DEMO_CHECK_PAYLOAD = TASK1_HELLO_BLOCKS
