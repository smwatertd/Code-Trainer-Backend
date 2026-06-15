"""Capstone placeholder tasks from final_course_270_tasks_with_placeholder_capstones.pdf (331–333)."""

from __future__ import annotations

TaskRow = dict


def _row(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    payload: dict,
) -> TaskRow:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "task_type": "task_fill_placeholders",
        "visibility": "public",
        "workflow_status": "active",
        "is_deleted": False,
        "payload": payload,
    }


def _tc(input_data: str, output: str) -> dict[str, str]:
    return {"input": input_data, "output": output}


def build_placeholder_capstones_catalog() -> list[TaskRow]:
    purchase_examples = {
        "python": (
            "name = input()\n"
            "price = float(input())\n"
            "count = int(input())\n"
            "total = price * count\n"
            "if total >= 0:\n"
            "    print(name, total)\n"
            "else:\n"
            "    print(name, 0)"
        ),
        "pascal": (
            "var name: string; price: real; count, total: integer;\n"
            "begin\n"
            "  readln(name);\n"
            "  readln(price);\n"
            "  readln(count);\n"
            "  total := trunc(price) * count;\n"
            "  if total >= 0 then writeln(name, ' ', total)\n"
            "  else writeln(name, ' ', 0);\n"
            "end."
        ),
    }

    return [
        _row(
            331,
            "Итог покупки с условием",
            (
                "Прочитайте название, цену и количество. Если итог не меньше нуля — выведите название и сумму, "
                "иначе выведите название и 0. Заполните пропуски в программе блоками из банка."
            ),
            "medium",
            {
                "language": "python",
                "target_language": "python",
                "source_language": "python",
                "placeholder_template": (
                    "name = ___()\n"
                    "price = ___(input())\n"
                    "count = ___(input())\n"
                    "total = price * count\n"
                    "if total ___ 0:\n"
                    "    print(name, total)\n"
                    "else:\n"
                    "    print(name, 0)"
                ),
                "placeholder_bank": ["input", "float", "int", ">=", ">", "print", "readln"],
                "test_cases": [
                    _tc("apple\n120\n3\n", "apple 360"),
                    _tc("book\n10\n0\n", "book 0"),
                    _tc("pen\n5\n8\n", "pen 40"),
                ],
                "constructions": [
                    "stdin_read",
                    "typed_declaration",
                    "assignment",
                    "arithmetic_ops",
                    "stdout_write",
                    "if_statement",
                ],
                "code_examples": purchase_examples,
            },
        ),
        _row(
            332,
            "Сумма двух чисел с условием",
            (
                "Прочитайте название и два числа. Если сумма не меньше нуля — выведите название и сумму, "
                "иначе выведите название и 0. Заполните пропуски в Pascal-программе."
            ),
            "medium",
            {
                "language": "pascal",
                "target_language": "pascal",
                "source_language": "python",
                "placeholder_template": (
                    "var name: string; a,b,total: integer;\n"
                    "begin\n"
                    "  readln(name);\n"
                    "  readln(a);\n"
                    "  readln(b);\n"
                    "  total ___ a + b;\n"
                    "  if total ___ 0 ___\n"
                    "    writeln(name, ' ', total)\n"
                    "  else\n"
                    "    writeln(name, ' ', 0);\n"
                    "end."
                ),
                "placeholder_bank": [":=", ">=", "then", "=", "do", "and"],
                "test_cases": [
                    _tc("Dune\n100\n0\n", "Dune 100"),
                    _tc("It\n50\n50\n", "It 100"),
                    _tc("Book\n0\n0\n", "Book 0"),
                ],
                "constructions": [
                    "stdin_read",
                    "typed_declaration",
                    "assignment",
                    "arithmetic_ops",
                    "stdout_write",
                    "if_statement",
                ],
                "code_examples": purchase_examples,
            },
        ),
        _row(
            333,
            "Сумма через cin",
            (
                "Прочитайте два числа, посчитайте сумму и выведите её, если сумма не меньше нуля. "
                "Заполните пропуски в C++-программе."
            ),
            "medium",
            {
                "language": "cpp",
                "target_language": "cpp",
                "source_language": "python",
                "placeholder_template": (
                    "#include <iostream>\n"
                    "int main(){\n"
                    "    int a, b, total;\n"
                    "    std::cin ___ a ___ b;\n"
                    "    total ___ a + b;\n"
                    "    if(total ___ 0){\n"
                    "        std::cout ___ total;\n"
                    "    }\n"
                    "    return 0;\n"
                    "}"
                ),
                "placeholder_bank": [">>", "<<", "=", "+=", ">", ">=", "then"],
                "test_cases": [
                    _tc("4\n6\n", "10"),
                    _tc("0\n0\n", "0"),
                    _tc("-2\n5\n", "3"),
                ],
                "constructions": [
                    "program_entry",
                    "stdin_read",
                    "typed_declaration",
                    "assignment",
                    "arithmetic_ops",
                    "stdout_write",
                    "if_statement",
                ],
                "code_examples": {
                    "python": "a = int(input())\nb = int(input())\ntotal = a + b\nif total >= 0:\n    print(total)",
                    "cpp": "#include <iostream>\nint main(){\n    int a,b,total;\n    std::cin >> a >> b;\n    total = a + b;\n    if(total >= 0) std::cout << total;\n    return 0;\n}",
                },
            },
        ),
    ]


PLACEHOLDER_CAPSTONES_SIZE = len(build_placeholder_capstones_catalog())
PLACEHOLDER_CAPSTONES_CATALOG = build_placeholder_capstones_catalog()
