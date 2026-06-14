from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "q7r8s9t0u1"
down_revision: Union[str, Sequence[str], None] = "p6q7r8s9t0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TASK2_VARIANTS = {
    "python": ["print('a')", "print('b')"],
    "cpp": ['cout << "a" << endl;', 'cout << "b" << endl;'],
    "pascal": ["WriteLn('a');", "WriteLn('b');"],
    "java": ['System.out.println("a");', 'System.out.println("b");'],
    "csharp": ['Console.WriteLine("a");', 'Console.WriteLine("b");'],
}

TASK5_VARIANTS = {
    "python": ["print(1)", "print(2)"],
    "cpp": ["cout << 1 << endl;", "cout << 2 << endl;"],
    "pascal": ["WriteLn(1);", "WriteLn(2);"],
    "java": ["System.out.println(1);", "System.out.println(2);"],
    "csharp": ["Console.WriteLine(1);", "Console.WriteLine(2);"],
}


def _merge_payload(current: dict, patch: dict) -> dict:
    merged = dict(current or {})
    merged.update(patch)
    return merged


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    patches = {
        2: {"blocks_by_language": TASK2_VARIANTS},
        5: {"blocks_by_language": TASK5_VARIANTS},
    }

    for task_id, patch in patches.items():
        row = connection.execute(
            sa.text(f'SELECT payload FROM "{schema}"."tasks" WHERE id = :id'),
            {"id": task_id},
        ).one_or_none()
        if row is None:
            continue
        payload = _merge_payload(row.payload, patch)
        connection.execute(
            sa.text(f'UPDATE "{schema}"."tasks" SET payload = CAST(:payload AS JSON) WHERE id = :id'),
            {"id": task_id, "payload": json.dumps(payload)},
        )


def downgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    for task_id in (2, 5):
        row = connection.execute(
            sa.text(f'SELECT payload FROM "{schema}"."tasks" WHERE id = :id'),
            {"id": task_id},
        ).one_or_none()
        if row is None:
            continue
        payload = dict(row.payload or {})
        payload.pop("blocks_by_language", None)
        connection.execute(
            sa.text(f'UPDATE "{schema}"."tasks" SET payload = CAST(:payload AS JSON) WHERE id = :id'),
            {"id": task_id, "payload": json.dumps(payload)},
        )
