from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "j0k1l2m3n4h8"
down_revision: Union[str, Sequence[str], None] = "i9j0k1l2m3g7"
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
                "id": 7,
                "title": "C++ for-loop snippet",
                "description": "Use a for loop in C++.",
                "difficulty": "easy",
                "task_type": "translation",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "kind": "snippet",
                    "target_language": "cpp",
                    "constructions": ["for_loop"],
                },
            },
            {
                "id": 8,
                "title": "Pascal for-loop snippet",
                "description": "Use a for loop in Pascal.",
                "difficulty": "easy",
                "task_type": "translation",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "kind": "snippet",
                    "target_language": "pascal",
                    "constructions": ["for_loop"],
                },
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id IN (7, 8)'))
