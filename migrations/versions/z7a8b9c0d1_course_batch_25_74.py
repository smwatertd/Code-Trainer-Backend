from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import COURSE_BATCH_PREV_SIZE, TASK_CATALOG_SEED

revision: str = "z7a8b9c0d1_course_batch_25_74"
down_revision: Union[str, Sequence[str], None] = "y6z7a8b9c0_input_output_12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

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
    for task in TASK_CATALOG_SEED:
        if task["id"] <= COURSE_BATCH_PREV_SIZE:
            continue
        row = dict(task)
        row["payload"] = json.loads(json.dumps(row["payload"]))
        rows.append(row)

    if not rows:
        raise RuntimeError("No course batch tasks found in TASK_CATALOG_SEED")

    existing = connection.execute(
        sa.text(f'SELECT id FROM "{schema}"."tasks" WHERE id > :min_id LIMIT 1'),
        {"min_id": COURSE_BATCH_PREV_SIZE},
    ).first()
    if existing:
        return

    op.bulk_insert(tasks, rows)

    next_id = max(row["id"] for row in rows) + 1
    connection.execute(
        sa.text(f'ALTER SEQUENCE "{schema}"."tasks_id_seq" RESTART WITH {next_id}')
    )


def downgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    connection.execute(
        sa.text(f'DELETE FROM "{schema}"."tasks" WHERE id > {COURSE_BATCH_PREV_SIZE}')
    )
    connection.execute(
        sa.text(
            f'ALTER SEQUENCE "{schema}"."tasks_id_seq" RESTART WITH {COURSE_BATCH_PREV_SIZE + 1}'
        )
    )
