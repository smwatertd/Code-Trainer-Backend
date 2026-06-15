from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import TASK_CATALOG_SEED
from migrations.seeds.tc42_curriculum_links import CURRICULUM_LINKS_SEED

revision: str = "i7j8k9l0_tc42_128_catalog"
down_revision: Union[str, Sequence[str], None] = "h6i6j7k8_diversify_lang_tracks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _delete_task_related(connection, schema: str) -> None:
    connection.execute(sa.text(f'DELETE FROM "{schema}"."submission_test_result"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."submission_lint_error"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."submission_pattern_error"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."submission"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."task_progress"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."student_curriculum_progress"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."task_curriculum_link"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."assignment_set_item"'))
    connection.execute(sa.text(f'DELETE FROM "{schema}"."tasks"'))


def _reset_tasks_sequence(connection, schema: str) -> None:
    connection.execute(sa.text(f'ALTER SEQUENCE "{schema}"."tasks_id_seq" RESTART WITH 1'))


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    _delete_task_related(connection, schema)
    _reset_tasks_sequence(connection, schema)

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
        row = dict(task)
        row["payload"] = json.loads(json.dumps(row["payload"]))
        rows.append(row)

    if len(rows) != 128:
        raise RuntimeError(f"Expected 128 TC42 tasks, got {len(rows)}")

    op.bulk_insert(tasks, rows)

    links = sa.table(
        "task_curriculum_link",
        sa.column("task_id", sa.Integer),
        sa.column("language", sa.String),
        sa.column("learning_concept_id", sa.String),
        sa.column("technical_concept_id", sa.String),
        sa.column("exercise_pattern_id", sa.String),
        sa.column("action", sa.String),
        sa.column("is_primary", sa.Boolean),
        schema=schema,
    )
    op.bulk_insert(links, CURRICULUM_LINKS_SEED)

    next_id = max(row["id"] for row in rows) + 1
    connection.execute(
        sa.text(f'ALTER SEQUENCE "{schema}"."tasks_id_seq" RESTART WITH {next_id}'),
    )


def downgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    _delete_task_related(connection, schema)
    _reset_tasks_sequence(connection, schema)
