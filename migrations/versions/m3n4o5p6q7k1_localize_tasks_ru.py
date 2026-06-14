from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "m3n4o5p6q7k1"
down_revision: Union[str, Sequence[str], None] = "l2m3n4o5p6j0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TASKS_RU: list[tuple[int, str, str]] = [
    (1, "Приветствие", "Переведите программу приветствия с Python на целевой язык."),
    (2, "Упорядочить вывод", "Расставьте блоки кода в правильном порядке."),
    (3, "Блок-схема if/else", "Постройте блок-схему для программы с ветвлением if/else."),
    (4, "Вывод с циклом for", "Напишите программу с циклом for для вывода чисел."),
    (5, "Упорядочить print", "Расставьте блоки print в порядке и проверьте вывод программы."),
    (6, "Блок-схема «Привет»", "Нарисуйте блок-схему программы приветствия и проверьте вывод."),
    (7, "Цикл for на C++", "Используйте цикл for в фрагменте кода на C++."),
    (8, "Цикл for на Pascal", "Используйте цикл for в фрагменте кода на Pascal."),
    (9, "Вывод в цикле (C++)", "Выведите числа от 0 до 2 с помощью цикла for на C++."),
    (10, "Вывод в цикле (Pascal)", "Выведите числа от 1 до 3 с помощью цикла for на Pascal."),
]

TASKS_EN: list[tuple[int, str, str]] = [
    (1, "Hello translation", "Translate a greeting from Python to target language."),
    (2, "Reorder prints", "Put code blocks in the correct order."),
    (3, "If diagram from code", "Build a flowchart for a simple if/else program."),
    (4, "Print with for-loop", "Use a for loop to print numbers."),
    (5, "Reorder numbered prints", "Put print blocks in order and verify program output."),
    (6, "Hello diagram with runtime check", "Draw a flowchart for a hello program and verify output."),
    (7, "C++ for-loop snippet", "Use a for loop in C++."),
    (8, "Pascal for-loop snippet", "Use a for loop in Pascal."),
    (9, "C++ loop output", "Print numbers 0..2 using a for loop."),
    (10, "Pascal loop output", "Print numbers 1..3 using a for loop."),
]


def _update_tasks(rows: list[tuple[int, str, str]]) -> None:
    schema = get_schema()
    for task_id, title, description in rows:
        op.execute(
            sa.text(
                f'UPDATE "{schema}"."tasks" SET title = :title, description = :description WHERE id = :id'
            ).bindparams(title=title, description=description, id=task_id),
        )


def upgrade() -> None:
    _update_tasks(TASKS_RU)


def downgrade() -> None:
    _update_tasks(TASKS_EN)
