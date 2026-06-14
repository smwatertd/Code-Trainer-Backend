from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "l2m3n4o5p6j0"
down_revision: Union[str, Sequence[str], None] = "k1l2m3n4o5i9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()

    op.create_table(
        "study_group",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], [f"{schema}.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_study_group_teacher_id", "study_group", ["teacher_id"], schema=schema)

    op.create_table(
        "group_member",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], [f"{schema}.study_group.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], [f"{schema}.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("group_id", "student_id"),
        schema=schema,
    )

    op.create_table(
        "group_invitation_code",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], [f"{schema}.study_group.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], [f"{schema}.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        schema=schema,
    )
    op.create_index(
        "ix_group_invitation_code_code",
        "group_invitation_code",
        ["code"],
        unique=True,
        schema=schema,
    )
    op.create_index(
        "ix_group_invitation_code_group_id",
        "group_invitation_code",
        ["group_id"],
        schema=schema,
    )

    op.create_table(
        "assignment_set",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("visibility", sa.String(length=16), server_default="private", nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_archived", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], [f"{schema}.study_group.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["teacher_id"], [f"{schema}.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_assignment_set_teacher_id", "assignment_set", ["teacher_id"], schema=schema)
    op.create_index("ix_assignment_set_group_id", "assignment_set", ["group_id"], schema=schema)

    op.create_table(
        "assignment_set_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assignment_set_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["assignment_set_id"], [f"{schema}.assignment_set.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], [f"{schema}.tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("assignment_set_id", "task_id", name="uq_assignment_set_item_set_task"),
        schema=schema,
    )
    op.create_index(
        "ix_assignment_set_item_assignment_set_id",
        "assignment_set_item",
        ["assignment_set_id"],
        schema=schema,
    )


def downgrade() -> None:
    schema = get_schema()
    op.drop_index("ix_assignment_set_item_assignment_set_id", table_name="assignment_set_item", schema=schema)
    op.drop_table("assignment_set_item", schema=schema)
    op.drop_index("ix_assignment_set_group_id", table_name="assignment_set", schema=schema)
    op.drop_index("ix_assignment_set_teacher_id", table_name="assignment_set", schema=schema)
    op.drop_table("assignment_set", schema=schema)
    op.drop_index("ix_group_invitation_code_group_id", table_name="group_invitation_code", schema=schema)
    op.drop_index("ix_group_invitation_code_code", table_name="group_invitation_code", schema=schema)
    op.drop_table("group_invitation_code", schema=schema)
    op.drop_table("group_member", schema=schema)
    op.drop_index("ix_study_group_teacher_id", table_name="study_group", schema=schema)
    op.drop_table("study_group", schema=schema)
