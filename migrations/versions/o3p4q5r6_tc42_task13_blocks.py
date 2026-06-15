"""Resync TC42 task 13 with normalized python block references."""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import TASK_CATALOG_SEED

revision: str = "o3p4q5r6_tc42_task13"
down_revision: Union[str, Sequence[str], None] = "n2o3p4q5_tc42_fix_13_18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    by_id = {task["id"]: task for task in TASK_CATALOG_SEED}
    task = by_id.get(13)
    if not task:
        return
    connection.execute(
        sa.text(
            f'UPDATE "{schema}"."tasks" '
            "SET payload = :payload "
            "WHERE id = :task_id"
        ),
        {
            "task_id": 13,
            "payload": json.dumps(task["payload"]),
        },
    )


def downgrade() -> None:
    pass
