"""Sync TC42 task payloads (placeholder references, debug target_language)."""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import TASK_CATALOG_SEED

revision: str = "k9l0m1n2_tc42_sync"
down_revision: Union[str, Sequence[str], None] = "j8k9l0m1_fix_task12_test_cases"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    for task in TASK_CATALOG_SEED:
        connection.execute(
            sa.text(
                f'UPDATE "{schema}"."tasks" '
                "SET payload = :payload, title = :title, description = :description, "
                "difficulty = :difficulty, task_type = :task_type "
                "WHERE id = :task_id"
            ),
            {
                "task_id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "difficulty": task["difficulty"],
                "task_type": task["task_type"],
                "payload": json.dumps(task["payload"]),
            },
        )


def downgrade() -> None:
    pass
