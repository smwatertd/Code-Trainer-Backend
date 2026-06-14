from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "e5f6a4b5c6d3"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a3b4c2"
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
                "id": 3,
                "title": "If diagram from code",
                "description": "Build a flowchart for a simple if/else program.",
                "difficulty": "easy",
                "task_type": "task_flowchart_to_code",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "flowchart_mode": "code_to_flowchart",
                    "flow_spec": {
                        "required_sequence": ["start", "input", "decision", "output", "output", "end"],
                        "required_text_checks": [
                            {"type": "input", "contains_any": ["readln", "n"]},
                            {"type": "decision", "contains_any": ["> 0"]},
                            {"type": "output", "contains_any": ["pos"]},
                            {"type": "output", "contains_any": ["nonpos"]},
                        ],
                        "allow_extra_nodes": False,
                    },
                    "constructions": ["if_statement"],
                },
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id = 3'))
