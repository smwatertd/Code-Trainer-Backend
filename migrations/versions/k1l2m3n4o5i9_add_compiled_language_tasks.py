from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "k1l2m3n4o5i9"
down_revision: Union[str, Sequence[str], None] = "j0k1l2m3n4h8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    tasks = sa.table(
        "tasks",
        sa.column("id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("difficulty", sa.String),
        sa.column("task_type", sa.String),
        sa.column("visibility", sa.String),
        sa.column("workflow_status", sa.String),
        sa.column("is_deleted", sa.Boolean),
        sa.column("payload", sa.JSON),
        schema=schema,
    )

    op.bulk_insert(
        tasks,
        [
            {
                "id": 9,
                "title": "C++ loop output",
                "description": "Print numbers 0..2 using a for loop.",
                "difficulty": "easy",
                "task_type": "translation",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "target_language": "cpp",
                    "constructions": ["for_loop"],
                    "test_cases": [{"inputs": "", "output": "0\n1\n2"}],
                },
            },
            {
                "id": 10,
                "title": "Pascal loop output",
                "description": "Print numbers 1..3 using a for loop.",
                "difficulty": "easy",
                "task_type": "translation",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "target_language": "pascal",
                    "constructions": ["for_loop"],
                    "test_cases": [{"inputs": "", "output": "1\n2\n3"}],
                },
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id IN (9, 10)'))
