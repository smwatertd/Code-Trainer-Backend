"""Multi-language curriculum tracks: primary link per (task_id, language) + basic program links."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.basic_program_curriculum_links import CURRICULUM_LINKS_SEED

revision: str = "g4h5i6j7k8_multilang_tracks"
down_revision: Union[str, Sequence[str], None] = "f3a4b5c6d7_prog_links"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    op.drop_constraint(
        "uq_task_curriculum_link_task_pattern",
        "task_curriculum_link",
        type_="unique",
        schema=schema,
    )
    op.create_unique_constraint(
        "uq_task_curriculum_link_task_pattern",
        "task_curriculum_link",
        ["task_id", "language", "exercise_pattern_id"],
        schema=schema,
    )

    op.drop_index(
        "uq_task_curriculum_link_primary",
        table_name="task_curriculum_link",
        schema=schema,
    )
    op.create_index(
        "uq_task_curriculum_link_primary",
        "task_curriculum_link",
        ["task_id", "language"],
        unique=True,
        schema=schema,
        postgresql_where=sa.text("is_primary = true"),
    )

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

    op.drop_index(
        "uq_task_curriculum_link_primary",
        table_name="task_curriculum_link",
        schema=schema,
    )
    op.create_index(
        "uq_task_curriculum_link_primary",
        "task_curriculum_link",
        ["task_id"],
        unique=True,
        schema=schema,
        postgresql_where=sa.text("is_primary = true"),
    )

    op.drop_constraint(
        "uq_task_curriculum_link_task_pattern",
        "task_curriculum_link",
        type_="unique",
        schema=schema,
    )
    op.create_unique_constraint(
        "uq_task_curriculum_link_task_pattern",
        "task_curriculum_link",
        ["task_id", "exercise_pattern_id"],
        schema=schema,
    )
