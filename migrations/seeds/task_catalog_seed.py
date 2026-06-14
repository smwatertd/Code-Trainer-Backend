from __future__ import annotations

from migrations.seeds.block_helpers import block_reorder_payload

TaskRow = dict


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


def _translation(
    *,
    topics: list[str],
    difficulty: str = "easy",
    source_code: str | None = None,
    target_language: str = "python",
    test_cases: list[dict] | None = None,
    constructions: list[str] | None = None,
    kind: str | None = None,
    template: str = "",
) -> dict:
    payload: dict = {"topics": topics}
    if source_code is not None:
        payload["source_language"] = "python"
        payload["source_code"] = source_code
    if target_language:
        payload["target_language"] = target_language
    if template:
        payload["template"] = template
    if test_cases:
        payload["test_cases"] = test_cases
    if constructions:
        payload["constructions"] = constructions
    if kind:
        payload["kind"] = kind
    return payload


def _write_from_description(
    *,
    topics: list[str],
    target_language: str = "python",
    template: str = "",
    problem_statement: str | None = None,
    test_cases: list[dict] | None = None,
    constructions: list[str] | None = None,
) -> dict:
    payload: dict = {
        "topics": topics,
        "target_language": target_language,
    }
    if template:
        payload["template"] = template
    if problem_statement:
        payload["problem_statement"] = problem_statement
    if test_cases:
        payload["test_cases"] = test_cases
    if constructions:
        payload["constructions"] = constructions
    return payload


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
        "flowchart_mode": "code_to_flowchart",
        "flow_spec": {
            "required_sequence": sequence,
            "required_text_checks": text_checks,
            "allow_extra_nodes": allow_extra_nodes,
            "require_loop_back_edge": require_loop_back_edge,
        },
        "topics": topics,
    }
    if source_code:
        payload["source_language"] = "python"
        payload["source_code"] = source_code
    if test_cases:
        payload["test_cases"] = test_cases
    if constructions:
        payload["constructions"] = constructions
    return payload


def _core_tasks() -> list[TaskRow]:
    """Задачи 1–10: совместимы с существующими e2e-тестами."""
    return [
        _row(
            1,
            "Приветствие",
            "Переведите программу с Python на выбранный язык. Программа должна вывести ровно одно слово Hello.",
            "easy",
            "translation",
            _translation(
                topics=["basics", "io"],
                source_code="print('Hello')",
                target_language="python",
                test_cases=[{"inputs": "", "output": "Hello"}],
            ),
        ),
        _row(
            2,
            "Упорядочить вывод",
            "Расставьте блоки print так, чтобы программа сначала вывела b, затем a.",
            "easy",
            "task_build_from_blocks",
            block_reorder_payload(
                blocks=["print('a')", "print('b')"],
                correct_order=[1, 0],
                expected_code="print('b')\nprint('a')",
                output="b\na",
                topics=["basics", "io"],
            ),
        ),
        _row(
            3,
            "Блок-схема if/else",
            "Постройте блок-схему для программы с ветвлением if/else. Схема должна отражать проверку знака числа.",
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
                source_code=("n = int(input())\n" "if n > 0:\n" "    print('pos')\n" "else:\n" "    print('nonpos')"),
                test_cases=[
                    {"inputs": "5\n", "output": "pos\n"},
                    {"inputs": "-2\n", "output": "nonpos\n"},
                ],
                constructions=["if_statement"],
            ),
        ),
        _row(
            4,
            "Вывод с циклом for",
            "Напишите программу с циклом for, которая выводит числа 0, 1 и 2 — каждое с новой строки.",
            "easy",
            "task_write_from_description",
            _write_from_description(
                topics=["loops"],
                target_language="python",
                constructions=["for_loop"],
                test_cases=[{"inputs": "", "output": "0\n1\n2"}],
            ),
        ),
        _row(
            5,
            "Упорядочить print",
            "Расставьте блоки print в правильном порядке и убедитесь, что программа выводит 1, затем 2.",
            "easy",
            "task_build_from_blocks",
            block_reorder_payload(
                blocks=["print(1)", "print(2)"],
                correct_order=[0, 1],
                expected_code="print(1)\nprint(2)",
                output="1\n2",
                topics=["basics", "io"],
            ),
        ),
        _row(
            6,
            "Блок-схема «Привет»",
            "Нарисуйте блок-схему программы приветствия и напишите код, который выводит hello.",
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
        _row(
            7,
            "Цикл for на C++",
            "Дополните фрагмент кода на C++: используйте цикл for для обхода диапазона.",
            "easy",
            "translation",
            _translation(
                topics=["loops", "cpp"],
                target_language="cpp",
                kind="snippet",
                constructions=["for_loop"],
            ),
        ),
        _row(
            8,
            "Цикл for на Pascal",
            "Дополните фрагмент кода на Pascal: используйте цикл for для обхода диапазона.",
            "easy",
            "translation",
            _translation(
                topics=["loops", "pascal"],
                target_language="pascal",
                kind="snippet",
                constructions=["for_loop"],
            ),
        ),
        _row(
            9,
            "Вывод в цикле (C++)",
            "Напишите программу на C++, которая выводит 0, 1 и 2 с помощью цикла for.",
            "medium",
            "task_write_from_description",
            _write_from_description(
                topics=["loops", "cpp"],
                target_language="cpp",
                constructions=["for_loop"],
                test_cases=[{"inputs": "", "output": "0\n1\n2"}],
            ),
        ),
        _row(
            10,
            "Вывод в цикле (Pascal)",
            "Напишите программу на Pascal, которая выводит 1, 2 и 3 с помощью цикла for.",
            "medium",
            "task_write_from_description",
            _write_from_description(
                topics=["loops", "pascal"],
                target_language="pascal",
                constructions=["for_loop"],
                test_cases=[{"inputs": "", "output": "1\n2\n3"}],
            ),
        ),
    ]


def _extra_write_from_description_tasks() -> list[TaskRow]:
    specs = [
        (11, "Сумма двух чисел", "Прочитайте два целых числа и выведите их сумму.", "easy", "io", "", "5\n"),
        (
            12,
            "Чётные числа",
            "Выведите чётные числа от 0 до 4 включительно, каждое с новой строки.",
            "easy",
            "loops",
            "",
            "0\n2\n4\n",
        ),
        (13, "Максимум из двух", "Прочитайте два числа и выведите большее.", "easy", "conditions", "3\n7\n", "7\n"),
        (14, "Привет, мир", "Выведите строку Hello, world!", "easy", "basics", "", "Hello, world!\n"),
        (15, "Обратный отсчёт", "Выведите числа 3, 2, 1 — каждое с новой строки.", "easy", "loops", "", "3\n2\n1\n"),
        (
            16,
            "Положительное число",
            "Прочитайте число. Если оно больше нуля, выведите yes, иначе no.",
            "easy",
            "conditions",
            "5\n",
            "yes\n",
        ),
        (17, "Слово «код»", "Выведите слово code.", "easy", "basics", "", "code\n"),
        (
            18,
            "Таблица умножения на 5",
            "Выведите результаты умножения 5×1, 5×2, 5×3.",
            "medium",
            "loops",
            "",
            "5\n10\n15\n",
        ),
        (19, "Сумма от 1 до 3", "Выведите сумму чисел 1, 2 и 3.", "easy", "loops", "", "6\n"),
        (
            20,
            "Модуль числа",
            "Прочитайте число и выведите его абсолютное значение.",
            "medium",
            "conditions",
            "-4\n",
            "4\n",
        ),
        (21, "Квадрат числа", "Прочитайте n и выведите n².", "medium", "basics", "3\n", "9\n"),
        (22, "Первые буквы", "Выведите две строки: A и B.", "easy", "io", "", "A\nB\n"),
        (
            23,
            "While: три раза",
            "Используйте цикл while, чтобы три раза вывести go.",
            "medium",
            "loops",
            "",
            "go\ngo\ngo\n",
        ),
        (
            24,
            "Сравнение строк",
            "Прочитайте слово. Если это yes, выведите ok.",
            "medium",
            "conditions",
            "yes\n",
            "ok\n",
        ),
        (25, "Факториал 4", "Выведите факториал числа 4 (24).", "hard", "loops", "", "24\n"),
        (26, "Сумма списка", "Выведите сумму чисел 2, 3 и 5.", "medium", "loops", "", "10\n"),
        (
            27,
            "Перевод: привет на Pascal",
            "По образцу Python выведите Hi на Pascal.",
            "medium",
            "pascal",
            "print('Hi')",
            "Hi\n",
        ),
        (28, "Перевод: двойной вывод", "Выведите два числа: 10 и 20.", "easy", "io", "", "10\n20\n"),
        (29, "Цикл до 5", "Выведите числа от 1 до 5.", "medium", "loops", "", "1\n2\n3\n4\n5\n"),
        (
            30,
            "Проверка чётности",
            "Прочитайте число. Выведите even для чётного, odd для нечётного.",
            "hard",
            "conditions",
            "4\n",
            "even\n",
        ),
    ]
    rows: list[TaskRow] = []
    for task_id, title, desc, diff, topic, stdin, stdout in specs:
        is_translation = task_id == 27
        payload_fn = _translation if is_translation else _write_from_description
        payload_kwargs: dict = {
            "topics": [topic, "io"] if topic != "io" else ["io", "basics"],
            "test_cases": [{"inputs": stdin, "output": stdout.strip()}],
        }
        if is_translation:
            payload_kwargs["source_code"] = "print('Hi')"
            payload_kwargs["target_language"] = "pascal"
        else:
            payload_kwargs["target_language"] = "python"
            if topic == "loops" and diff != "easy":
                payload_kwargs["constructions"] = ["for_loop"]

        rows.append(
            _row(
                task_id,
                title,
                desc,
                diff,
                "translation" if is_translation else "task_write_from_description",
                payload_fn(**payload_kwargs),
            )
        )
    return rows


def _extra_block_reorder_tasks() -> list[TaskRow]:
    specs = [
        (
            31,
            "Порядок: start → finish",
            "Расставьте блоки так, чтобы сначала выводилось start, затем finish.",
            "easy",
            ["print('start')", "print('finish')"],
            [0, 1],
            "start\nfinish",
        ),
        (
            32,
            "Порядок: 3 и 1",
            "Расставьте блоки: сначала 3, потом 1.",
            "easy",
            ["print(1)", "print(3)"],
            [1, 0],
            "3\n1",
        ),
        (
            33,
            "Порядок: red, green",
            "Сначала red, затем green.",
            "easy",
            ["print('green')", "print('red')"],
            [1, 0],
            "red\ngreen",
        ),
        (
            34,
            "Инициализация и вывод",
            "Сначала объявите x = 0, затем выведите x.",
            "medium",
            ["x = 0", "print(x)"],
            [0, 1],
            "0",
        ),
        (
            35,
            "Три строки",
            "Выведите alpha, beta, gamma в этом порядке.",
            "medium",
            ["print('gamma')", "print('alpha')", "print('beta')"],
            [1, 2, 0],
            "alpha\nbeta\ngamma",
        ),
        (
            36,
            "Числа по убыванию",
            "Выведите 9, затем 6, затем 3.",
            "medium",
            ["print(3)", "print(9)", "print(6)"],
            [1, 2, 0],
            "9\n6\n3",
        ),
        (
            37,
            "Логические блоки",
            "Сначала True, затем False.",
            "medium",
            ["print(False)", "print(True)"],
            [1, 0],
            "True\nFalse",
        ),
        (
            38,
            "Четыре шага",
            "Выведите step1, step2, step3, step4 по порядку.",
            "hard",
            ["print('step4')", "print('step2')", "print('step1')", "print('step3')"],
            [2, 1, 3, 0],
            "step1\nstep2\nstep3\nstep4",
        ),
    ]
    rows: list[TaskRow] = []
    for task_id, title, desc, diff, blocks, order, output in specs:
        expected = "\n".join(blocks[i] for i in order)
        rows.append(
            _row(
                task_id,
                title,
                desc,
                diff,
                "task_build_from_blocks",
                block_reorder_payload(
                    blocks=blocks,
                    correct_order=order,
                    expected_code=expected,
                    output=output,
                    topics=["basics", "io"] if diff == "easy" else ["loops", "io"],
                ),
            )
        )
    return rows


FLOWCHART_TEST_CASES: dict[int, list[dict[str, str]]] = {
    39: [{"inputs": "Ana\n", "output": "Ana\n"}],
    40: [{"inputs": "", "output": "0\n1\n2\n"}],
    41: [{"inputs": "", "output": "1\n2\n"}],
    42: [{"inputs": "yes\n", "output": "yes\n"}, {"inputs": "no\n", "output": "no\n"}],
    43: [{"inputs": "5\n3\n", "output": "8\n"}],
    44: [{"inputs": "", "output": "3\n2\n1\n"}],
    45: [{"inputs": "", "output": "hi\n"}],
    46: [{"inputs": "3\n7\n", "output": "3\n"}, {"inputs": "9\n2\n", "output": "2\n"}],
    47: [{"inputs": "", "output": "1\n"}],
    48: [{"inputs": "secret\n", "output": "ok\n"}, {"inputs": "wrong\n", "output": "denied\n"}],
    49: [{"inputs": "", "output": "2\n4\n6\n"}],
    50: [{"inputs": "", "output": "done\n"}],
}


def _extra_flowchart_tasks() -> list[TaskRow]:
    specs = [
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
            "Постройте цикл for: «Цикл» → «Вывод» → стрелка обратно в «Цикл»; из «Цикл» также выход в «Конец».",
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
            "Постройте цикл while по программе: блок «Действие» можно поставить перед циклом (инициализация). "
            "Из «Цикла» — в тело (слева), обратно — справа или через верх; выход — снизу.",
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
            "Постройте цикл for: «Цикл» → «Процесс» → «Вывод» → обратно в «Цикл»; из «Цикл» также в «Конец».",
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
    rows: list[TaskRow] = []
    for spec in specs:
        allow_extra = False
        require_loop_back = False
        if len(spec) == 10:
            (
                task_id,
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
            task_id, title, desc, diff, sequence, checks, constructions, source_code, allow_extra = spec
        else:
            task_id, title, desc, diff, sequence, checks, constructions, source_code = spec
        rows.append(
            _row(
                task_id,
                title,
                desc,
                diff,
                "task_flowchart_to_code",
                _flowchart(
                    topics=(
                        ["flowchart", "loops"]
                        if "loop" in sequence
                        else ["flowchart", "conditions"] if "decision" in sequence else ["flowchart", "basics"]
                    ),
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


def build_task_catalog() -> list[TaskRow]:
    tasks = [
        *_core_tasks(),
        *_extra_write_from_description_tasks(),
        *_extra_block_reorder_tasks(),
        *_extra_flowchart_tasks(),
    ]
    if len(tasks) != 50:
        raise RuntimeError(f"Expected 50 tasks, got {len(tasks)}")
    return tasks


CURRICULUM_LINKS = [
    {
        "task_id": 4,
        "language": "python",
        "learning_concept_id": "loops",
        "technical_concept_id": "for_loop",
        "exercise_pattern_id": "tr_pattern_translation",
        "action": "implement",
        "is_primary": True,
    },
]

TASK_CATALOG_SEED = build_task_catalog()
