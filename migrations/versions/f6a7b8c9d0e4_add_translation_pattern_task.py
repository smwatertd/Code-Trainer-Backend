from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "f6a7b8c9d0e4"
down_revision: Union[str, Sequence[str], None] = "e5f6a4b5c6d3"
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
                "id": 4,
                "title": "Print with for-loop",
                "description": "Use a for loop to print numbers.",
                "difficulty": "easy",
                "task_type": "translation",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "source_language": "python",
                    "target_language": "python",
                    "constructions": ["for_loop"],
                    "test_cases": [
                        {"inputs": "", "output": "0\n1\n2"},
                    ],
                },
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id = 4'))
