from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database.base import Base, utc_now


class TaskProgressModel(Base):
    __tablename__ = "task_progress"
    __table_args__ = (sa.UniqueConstraint("user_id", "task_id", name="uq_task_progress_user_task"),)

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
    attempts_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    passed_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    last_status: Mapped[str | None] = mapped_column(sa.String(16), nullable=True)
    last_submission_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    first_passed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class TaskCurriculumLinkModel(Base):
    __tablename__ = "task_curriculum_link"
    __table_args__ = (
        sa.UniqueConstraint(
            "task_id",
            "language",
            "exercise_pattern_id",
            name="uq_task_curriculum_link_task_pattern",
        ),
        sa.Index(
            "uq_task_curriculum_link_primary",
            "task_id",
            "language",
            unique=True,
            postgresql_where=sa.text("is_primary = true"),
        ),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    learning_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    technical_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    exercise_pattern_id: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    action: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    is_primary: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False, server_default=sa.false())
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class StudentCurriculumProgressModel(Base):
    __tablename__ = "student_curriculum_progress"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "task_id", name="uq_student_curriculum_progress_user_task"),
        sa.Index("ix_student_curriculum_progress_user_lc", "user_id", "language", "learning_concept_id"),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[int] = mapped_column(
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    learning_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    technical_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    action: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    exercise_pattern_id: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    attempts_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    passed_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    last_status: Mapped[str | None] = mapped_column(sa.String(16), nullable=True)
    last_submission_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    first_passed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
