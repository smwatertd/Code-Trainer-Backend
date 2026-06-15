"""Fix TC42 tasks 13 test cases and task 18 placeholder content."""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import TASK_CATALOG_SEED

revision: str = "n2o3p4q5_tc42_fix_13_18"
down_revision: Union[str, Sequence[str], None] = "m1n2o3p4_tc42_resync"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    by_id = {task["id"]: task for task in TASK_CATALOG_SEED}

    for task_id in (13, 18):
        task = by_id.get(task_id)
        if not task:
            continue
        connection.execute(
            sa.text(
                f'UPDATE "{schema}"."tasks" '
                "SET payload = :payload, title = :title, description = :description, "
                "difficulty = :difficulty, task_type = :task_type "
                "WHERE id = :task_id"
            ),
            {
                "task_id": task_id,
                "title": task["title"],
                "description": task["description"],
                "difficulty": task["difficulty"],
                "task_type": task["task_type"],
                "payload": json.dumps(task["payload"]),
            },
        )


def downgrade() -> None:
    pass
