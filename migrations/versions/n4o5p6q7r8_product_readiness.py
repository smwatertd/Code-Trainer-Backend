from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "n4o5p6q7r8"
down_revision: Union[str, Sequence[str], None] = "m3n4o5p6q7k1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _merge_payload(current: dict, patch: dict) -> dict:
    merged = dict(current or {})
    merged.update(patch)
    return merged


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    op.add_column(
        "submission_test_result",
        sa.Column("duration_ms", sa.Integer(), server_default="0", nullable=False),
        schema=schema,
    )
    op.add_column(
        "submission",
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        schema=schema,
    )
    op.add_column(
        "tasks",
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        schema=schema,
    )
    op.create_foreign_key(
        "fk_tasks_owner_user_id",
        "tasks",
        "user",
        ["owner_user_id"],
        ["id"],
        source_schema=schema,
        referent_schema=schema,
        ondelete="SET NULL",
    )

    task_patches: dict[int, dict] = {
        1: {
            "title": "Приветствие",
            "description": (
                "Переведите программу с Python на выбранный язык. " "Программа должна вывести ровно одно слово Hello."
            ),
            "payload": {
                "test_cases": [{"inputs": "", "output": "Hello"}],
                "topics": ["basics", "io"],
            },
        },
        2: {
            "title": "Упорядочить вывод",
            "description": ("Расставьте блоки print так, чтобы программа сначала вывела b, затем a."),
            "payload": {
                "test_cases": [{"inputs": "", "output": "b\na"}],
                "topics": ["basics", "io"],
            },
        },
        3: {
            "description": (
                "Постройте блок-схему для программы с ветвлением if/else. "
                "Схема должна отражать проверку знака числа и два разных вывода."
            ),
            "payload": {
                "topics": ["conditions", "flowchart"],
            },
        },
        4: {
            "description": "Напишите программу с циклом for, которая выводит числа 0, 1 и 2 — каждое с новой строки.",
            "payload": {"topics": ["loops"]},
        },
        5: {
            "description": "Расставьте блоки print в правильном порядке и убедитесь, что программа выводит 1, затем 2.",
            "payload": {"topics": ["basics", "io"]},
        },
        6: {
            "description": ("Нарисуйте блок-схему программы приветствия и напишите код, " "который выводит hello."),
            "payload": {"topics": ["flowchart", "io"]},
        },
        7: {
            "description": "Дополните фрагмент кода на C++: используйте цикл for для обхода диапазона.",
            "payload": {"topics": ["loops", "cpp"]},
        },
        8: {
            "description": "Дополните фрагмент кода на Pascal: используйте цикл for для обхода диапазона.",
            "payload": {"topics": ["loops", "pascal"]},
        },
        9: {
            "description": "Напишите программу на C++, которая выводит 0, 1 и 2 с помощью цикла for.",
            "payload": {"topics": ["loops", "cpp"]},
        },
        10: {
            "description": "Напишите программу на Pascal, которая выводит 1, 2 и 3 с помощью цикла for.",
            "payload": {"topics": ["loops", "pascal"]},
        },
    }

    for task_id, patch in task_patches.items():
        row = connection.execute(
            sa.text(f'SELECT title, description, payload FROM "{schema}"."tasks" WHERE id = :id'),
            {"id": task_id},
        ).one_or_none()
        if row is None:
            continue
        title = patch.get("title", row.title)
        description = patch.get("description", row.description)
        payload = _merge_payload(row.payload, patch.get("payload", {}))
        connection.execute(
            sa.text(
                f'UPDATE "{schema}"."tasks" '
                "SET title = :title, description = :description, payload = CAST(:payload AS JSON) "
                "WHERE id = :id"
            ),
            {
                "id": task_id,
                "title": title,
                "description": description,
                "payload": json.dumps(payload),
            },
        )


def downgrade() -> None:
    schema = get_schema()
    op.drop_constraint("fk_tasks_owner_user_id", "tasks", schema=schema, type_="foreignkey")
    op.drop_column("tasks", "owner_user_id", schema=schema)
    op.drop_column("submission", "duration_ms", schema=schema)
    op.drop_column("submission_test_result", "duration_ms", schema=schema)
