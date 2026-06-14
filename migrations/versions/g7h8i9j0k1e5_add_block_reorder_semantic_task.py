from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "g7h8i9j0k1e5"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e4"
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
                "id": 5,
                "title": "Reorder numbered prints",
                "description": "Put print blocks in order and verify program output.",
                "difficulty": "easy",
                "task_type": "task_build_from_blocks",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "language": "python",
                    "blocks": ["print(1)", "print(2)"],
                    "correct_order": [0, 1],
                    "expected_code": "print(1)\nprint(2)",
                    "test_cases": [{"inputs": "", "output": "1\n2"}],
                },
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id = 5'))
