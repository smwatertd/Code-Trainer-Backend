from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.base import Base, utc_now


class SubmissionModel(Base):
    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    code: Mapped[str] = mapped_column(sa.Text, nullable=False)
    input_payload: Mapped[dict | None] = mapped_column(sa.JSON(), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False, default="queued")
    success: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    linter_errors: Mapped[list[SubmissionLintErrorModel]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    pattern_errors: Mapped[list[SubmissionPatternErrorModel]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    test_results: Mapped[list[SubmissionTestResultModel]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )


class SubmissionLintErrorModel(Base):
    __tablename__ = "submission_lint_error"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    error_type: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    submission: Mapped[SubmissionModel] = relationship(back_populates="linter_errors")


class SubmissionPatternErrorModel(Base):
    __tablename__ = "submission_pattern_error"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    error_type: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    submission: Mapped[SubmissionModel] = relationship(back_populates="pattern_errors")


class SubmissionTestResultModel(Base):
    __tablename__ = "submission_test_result"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    inputs: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    expected: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    actual: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    message: Mapped[str] = mapped_column(sa.Text, default="", nullable=False)
    duration_ms: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    submission: Mapped[SubmissionModel] = relationship(back_populates="test_results")
