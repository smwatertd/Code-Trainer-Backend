from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.placeholder_capstones_catalog import PLACEHOLDER_CAPSTONES_CATALOG

revision: str = "e2f3a4b5c6_placeholder_capstones"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5_course_batch_225_270"
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

    rows = []
    for task in PLACEHOLDER_CAPSTONES_CATALOG:
        row = dict(task)
        row["payload"] = json.loads(json.dumps(row["payload"]))
        rows.append(row)

    op.bulk_insert(tasks, rows)


def downgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    task_ids = [task["id"] for task in PLACEHOLDER_CAPSTONES_CATALOG]
    ids_sql = ", ".join(str(task_id) for task_id in task_ids)
    connection.execute(sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id IN ({ids_sql})'))
