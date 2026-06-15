"""Distinct beginner track chapter plans per language."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.basic_program_curriculum_links import CURRICULUM_LINKS_SEED

revision: str = "h6i6j7k8_diversify_lang_tracks"
down_revision: Union[str, Sequence[str], None] = "h5i6j7k8_expand_tracks_24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    task_ids = sorted({row["task_id"] for row in CURRICULUM_LINKS_SEED})
    placeholders = ", ".join(str(task_id) for task_id in task_ids)
    connection.execute(
        sa.text(f'DELETE FROM "{schema}"."task_curriculum_link" WHERE task_id IN ({placeholders})'),
    )

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


def downgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    task_ids = sorted({row["task_id"] for row in CURRICULUM_LINKS_SEED})
    placeholders = ", ".join(str(task_id) for task_id in task_ids)
    connection.execute(
        sa.text(f'DELETE FROM "{schema}"."task_curriculum_link" WHERE task_id IN ({placeholders})'),
    )
