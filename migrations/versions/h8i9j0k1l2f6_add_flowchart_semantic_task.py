from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "h8i9j0k1l2f6"
down_revision: Union[str, Sequence[str], None] = "g7h8i9j0k1e5"
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
                "id": 6,
                "title": "Hello diagram with runtime check",
                "description": "Draw a flowchart for a hello program and verify output.",
                "difficulty": "easy",
                "task_type": "task_flowchart_to_code",
                "visibility": "public",
                "workflow_status": "active",
                "is_deleted": False,
                "payload": {
                    "flowchart_mode": "code_to_flowchart",
                    "flow_spec": {
                        "required_sequence": ["start", "output", "end"],
                        "required_text_checks": [
                            {"type": "output", "contains_any": ["hello"]},
                        ],
                        "allow_extra_nodes": False,
                    },
                    "test_cases": [{"inputs": "", "output": "hello"}],
                },
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id = 6'))
