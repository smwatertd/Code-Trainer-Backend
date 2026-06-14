from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "i9j0k1l2m3g7"
down_revision: Union[str, Sequence[str], None] = "h8i9j0k1l2f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()

    op.create_table(
        "task_curriculum_link",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("learning_concept_id", sa.String(length=64), nullable=False),
        sa.Column("technical_concept_id", sa.String(length=64), nullable=False),
        sa.Column("exercise_pattern_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], [f"{schema}.tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "exercise_pattern_id", name="uq_task_curriculum_link_task_pattern"),
        schema=schema,
    )
    op.create_index(
        "ix_task_curriculum_link_task_id",
        "task_curriculum_link",
        ["task_id"],
        unique=False,
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

    op.create_table(
        "student_curriculum_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("learning_concept_id", sa.String(length=64), nullable=False),
        sa.Column("technical_concept_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("exercise_pattern_id", sa.String(length=128), nullable=False),
        sa.Column("attempts_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("passed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_status", sa.String(length=16), nullable=True),
        sa.Column("last_submission_id", sa.Integer(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_passed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["last_submission_id"], [f"{schema}.submission.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_id"], [f"{schema}.tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], [f"{schema}.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "task_id", name="uq_student_curriculum_progress_user_task"),
        schema=schema,
    )
    op.create_index(
        "ix_student_curriculum_progress_user_lc",
        "student_curriculum_progress",
        ["user_id", "language", "learning_concept_id"],
        unique=False,
        schema=schema,
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
    op.bulk_insert(
        links,
        [
            {
                "task_id": 4,
                "language": "python",
                "learning_concept_id": "loops",
                "technical_concept_id": "for_loop",
                "exercise_pattern_id": "tr_pattern_translation",
                "action": "implement",
                "is_primary": True,
            },
        ],
    )


def downgrade() -> None:
    schema = get_schema()
    op.drop_index("ix_student_curriculum_progress_user_lc", table_name="student_curriculum_progress", schema=schema)
    op.drop_table("student_curriculum_progress", schema=schema)
    op.drop_index("uq_task_curriculum_link_primary", table_name="task_curriculum_link", schema=schema)
    op.drop_index("ix_task_curriculum_link_task_id", table_name="task_curriculum_link", schema=schema)
    op.drop_table("task_curriculum_link", schema=schema)
