"""Flowchart tasks for unit/e2e tests (not part of the 12-task public catalog)."""
from __future__ import annotations

TaskRow = dict

FLOWCHART_TEST_CASES: dict[int, list[dict[str, str]]] = {
    1039: [{"inputs": "Ana\n", "output": "Ana\n"}],
    1040: [{"inputs": "", "output": "0\n1\n2\n"}],
    1041: [{"inputs": "", "output": "1\n2\n"}],
    1042: [{"inputs": "yes\n", "output": "yes\n"}, {"inputs": "no\n", "output": "no\n"}],
    1043: [{"inputs": "5\n3\n", "output": "8\n"}],
    1044: [{"inputs": "", "output": "3\n2\n1\n"}],
    1045: [{"inputs": "", "output": "hi\n"}],
    1046: [{"inputs": "3\n7\n", "output": "3\n"}, {"inputs": "9\n2\n", "output": "2\n"}],
    1047: [{"inputs": "", "output": "1\n"}],
    1048: [{"inputs": "secret\n", "output": "ok\n"}, {"inputs": "wrong\n", "output": "denied\n"}],
    1049: [{"inputs": "", "output": "2\n4\n6\n"}],
    1050: [{"inputs": "", "output": "done\n"}],
}


def flowchart_test_id(legacy_id: int) -> int:
    return 1000 + legacy_id


FLOWCHART_SAMPLE_IDS = [flowchart_test_id(task_id) for task_id in [3, 6, *range(39, 51)]]


def _row(
    task_id: int,
    title: str,
    description: str,
    difficulty: str,
    task_type: str,
    payload: dict,
) -> TaskRow:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "task_type": task_type,
        "visibility": "public",
        "workflow_status": "active",
        "is_deleted": False,
        "payload": payload,
    }


def _flowchart(
    *,
    topics: list[str],
    difficulty: str,
    sequence: list[str],
    text_checks: list[dict],
    source_code: str | None = None,
    allow_extra_nodes: bool = False,
    require_loop_back_edge: bool = False,
    test_cases: list[dict] | None = None,
    constructions: list[str] | None = None,
) -> dict:
    payload: dict = {
        "topics": topics,
        "flowchart_mode": "code_to_flowchart",
        "flow_spec": {
            "required_sequence": sequence,
            "required_text_checks": text_checks,
            "allow_extra_nodes": allow_extra_nodes,
            "require_loop_back_edge": require_loop_back_edge,
        },
    }
    if source_code is not None:
        payload["source_language"] = "python"
        payload["source_code"] = source_code
    if test_cases:
        payload["test_cases"] = test_cases
    if constructions:
        payload["constructions"] = constructions
    return payload


def _extra_flowchart_specs() -> list[tuple]:
    return [
        (
            39,
            "Схема: ввод и вывод",
            "Постройте схему: начало → ввод → вывод → конец.",
            "easy",
            ["start", "input", "output", "end"],
            [
                {"type": "input", "contains_any": ["read", "input"]},
                {"type": "output", "contains_any": ["print", "write"]},
            ],
            None,
            "name = input()\nprint(name)",
        ),
        (
            40,
            "Схема: цикл for",
            "Постройте цикл for с обратной стрелкой.",
            "medium",
            ["start", "loop", "output", "end"],
            [
                {"type": "loop", "contains_any": ["for", "range", "<", ">"]},
                {"type": "output", "contains_any": ["print"]},
            ],
            ["for_loop"],
            "for i in range(3):\n    print(i)",
            False,
            True,
        ),
        (
            41,
            "Схема: два вывода",
            "Схема с двумя блоками вывода подряд.",
            "easy",
            ["start", "output", "output", "end"],
            [{"type": "output", "contains_any": ["1"]}, {"type": "output", "contains_any": ["2"]}],
            None,
            "print(1)\nprint(2)",
        ),
        (
            42,
            "Схема: ветвление",
            "Схема с условием yes/no.",
            "medium",
            ["start", "decision", "output", "output", "end"],
            [{"type": "decision", "contains_any": ["?"]}],
            ["if_statement"],
            "answer = input()\nif answer == 'yes':\n    print('yes')\nelse:\n    print('no')",
        ),
        (
            43,
            "Схема: сумма",
            "Схема программы, читающей два числа и выводящей сумму.",
            "medium",
            ["start", "input", "input", "process", "output", "end"],
            [{"type": "process", "contains_any": ["+"]}],
            None,
            "a = int(input())\nb = int(input())\nprint(a + b)",
        ),
        (
            44,
            "Схема: while",
            "Постройте цикл while по программе.",
            "hard",
            ["start", "loop", "output", "process", "end"],
            [
                {"type": "loop", "contains_any": ["while", ">"]},
                {"type": "output", "contains_any": ["print"]},
                {"type": "process", "contains_any": ["-=", "-"]},
            ],
            ["while_loop"],
            "n = 3\nwhile n > 0:\n    print(n)\n    n -= 1",
            False,
            True,
        ),
        (
            45,
            "Схема: функция",
            "Схема с вызовом функции.",
            "hard",
            ["start", "process", "output", "end"],
            [{"type": "process", "contains_any": ["def", "function"]}],
            ["function_definition"],
            "def greet():\n    return 'hi'\nprint(greet())",
        ),
        (
            46,
            "Схема: минимум",
            "Схема поиска минимума из двух чисел.",
            "hard",
            ["start", "input", "decision", "output", "output", "end"],
            [{"type": "decision", "contains_any": ["<"]}],
            ["if_statement"],
            "a = int(input())\nb = int(input())\nif a < b:\n    print(a)\nelse:\n    print(b)",
        ),
        (
            47,
            "Схема: счётчик",
            "Схема с счётчиком и выводом значения.",
            "medium",
            ["start", "process", "output", "end"],
            [{"type": "process", "contains_any": ["="]}],
            None,
            "count = 0\ncount = count + 1\nprint(count)",
        ),
        (
            48,
            "Схема: пароль",
            "Схема проверки пароля (ветвление).",
            "medium",
            ["start", "input", "decision", "output", "output", "end"],
            [
                {"type": "output", "contains_any": ["ok"]},
                {"type": "output", "contains_any": ["denied"]},
            ],
            ["if_statement"],
            "pwd = input()\nif pwd == 'secret':\n    print('ok')\nelse:\n    print('denied')",
        ),
        (
            49,
            "Схема: таблица",
            "Постройте цикл for с процессом и выводом.",
            "hard",
            ["start", "loop", "process", "output", "end"],
            [
                {"type": "loop", "contains_any": ["for", "range"]},
                {"type": "process", "contains_any": ["*"]},
                {"type": "output", "contains_any": ["print"]},
            ],
            ["for_loop"],
            "for i in range(1, 4):\n    print(i * 2)",
            False,
            True,
        ),
        (
            50,
            "Схема: завершение",
            "Минимальная схема: начало → процесс → конец.",
            "easy",
            ["start", "process", "end"],
            [{"type": "process", "contains_any": ["print", "write", "вывод"]}],
            None,
            "print('done')",
        ),
    ]


def build_flowchart_sample_tasks() -> list[TaskRow]:
    rows: list[TaskRow] = [
        _row(
            flowchart_test_id(3),
            "Блок-схема if/else",
            "Постройте блок-схему для программы с ветвлением if/else.",
            "easy",
            "task_flowchart_to_code",
            _flowchart(
                topics=["conditions", "flowchart"],
                difficulty="easy",
                sequence=["start", "input", "decision", "output", "output", "end"],
                text_checks=[
                    {"type": "input", "contains_any": ["readln", "n", "input"]},
                    {"type": "decision", "contains_any": ["> 0"]},
                    {"type": "output", "contains_any": ["pos"]},
                    {"type": "output", "contains_any": ["nonpos"]},
                ],
                source_code=(
                    "n = int(input())\n"
                    "if n > 0:\n"
                    "    print('pos')\n"
                    "else:\n"
                    "    print('nonpos')"
                ),
                test_cases=[
                    {"inputs": "5\n", "output": "pos\n"},
                    {"inputs": "-2\n", "output": "nonpos\n"},
                ],
                constructions=["if_statement"],
            ),
        ),
        _row(
            flowchart_test_id(6),
            "Блок-схема «Привет»",
            "Нарисуйте блок-схему программы приветствия.",
            "easy",
            "task_flowchart_to_code",
            _flowchart(
                topics=["flowchart", "io"],
                difficulty="easy",
                sequence=["start", "output", "end"],
                text_checks=[{"type": "output", "contains_any": ["hello"]}],
                source_code="print('hello')",
                test_cases=[{"inputs": "", "output": "hello"}],
            ),
        ),
    ]

    for spec in _extra_flowchart_specs():
        allow_extra = False
        require_loop_back = False
        if len(spec) == 10:
            (
                legacy_id,
                title,
                desc,
                diff,
                sequence,
                checks,
                constructions,
                source_code,
                allow_extra,
                require_loop_back,
            ) = spec
        elif len(spec) == 9:
            legacy_id, title, desc, diff, sequence, checks, constructions, source_code, allow_extra = spec
        else:
            legacy_id, title, desc, diff, sequence, checks, constructions, source_code = spec

        task_id = flowchart_test_id(legacy_id)
        topics = (
            ["flowchart", "loops"]
            if "loop" in sequence
            else ["flowchart", "conditions"]
            if "decision" in sequence
            else ["flowchart", "basics"]
        )
        rows.append(
            _row(
                task_id,
                title,
                desc,
                diff,
                "task_flowchart_to_code",
                _flowchart(
                    topics=topics,
                    difficulty=diff,
                    sequence=sequence,
                    text_checks=checks,
                    constructions=constructions,
                    source_code=source_code,
                    test_cases=FLOWCHART_TEST_CASES.get(task_id),
                    allow_extra_nodes=allow_extra,
                    require_loop_back_edge=require_loop_back,
                ),
            )
        )

    return rows


FLOWCHART_SAMPLE_CATALOG: dict[int, TaskRow] = {
    row["id"]: row for row in build_flowchart_sample_tasks()
}
