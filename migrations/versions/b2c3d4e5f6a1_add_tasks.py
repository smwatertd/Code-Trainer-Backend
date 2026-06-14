from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("difficulty", sa.String(length=32), server_default="easy", nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("visibility", sa.String(length=32), server_default="public", nullable=False),
        sa.Column("workflow_status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("payload", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )

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
                "id": 1,
                "title": "Hello translation",
                "description": "Translate a greeting from Python to target language.",
                "difficulty": "easy",
                "task_type": "translation",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "source_language": "python",
                    "target_language": "cpp",
                    "source_code": "print('Hello')",
                    "template": "",
                },
            },
            {
                "id": 2,
                "title": "Reorder prints",
                "description": "Put code blocks in the correct order.",
                "difficulty": "easy",
                "task_type": "task_build_from_blocks",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "language": "python",
                    "blocks": ["print('a')", "print('b')"],
                    "correct_order": [1, 0],
                    "expected_code": "print('b')\nprint('a')",
                },
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("tasks", schema=get_schema())
