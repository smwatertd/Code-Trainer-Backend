from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "d4e5f6a3b4c2"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()

    op.create_table(
        "task_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("attempts_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("passed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_status", sa.String(length=16), nullable=True),
        sa.Column("last_submission_id", sa.Integer(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_passed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["last_submission_id"], [f"{schema}.submission.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], [f"{schema}.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "task_id", name="uq_task_progress_user_task"),
        schema=schema,
    )
    op.create_index("ix_task_progress_user_id", "task_progress", ["user_id"], unique=False, schema=schema)
    op.create_index("ix_task_progress_task_id", "task_progress", ["task_id"], unique=False, schema=schema)


def downgrade() -> None:
    schema = get_schema()

    op.drop_index("ix_task_progress_task_id", table_name="task_progress", schema=schema)
    op.drop_index("ix_task_progress_user_id", table_name="task_progress", schema=schema)
    op.drop_table("task_progress", schema=schema)
