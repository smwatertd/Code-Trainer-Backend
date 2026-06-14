from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.base import Base, utc_now


class AssignmentSetModel(Base):
    __tablename__ = "assignment_set"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False, default="", server_default="")
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    visibility: Mapped[str] = mapped_column(sa.String(16), nullable=False, default="private", server_default="private")
    group_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("study_group.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    deadline_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    is_archived: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    items: Mapped[list[AssignmentSetItemModel]] = relationship(
        "AssignmentSetItemModel",
        lazy="selectin",
        order_by="AssignmentSetItemModel.sort_order",
    )


class AssignmentSetItemModel(Base):
    __tablename__ = "assignment_set_item"
    __table_args__ = (sa.UniqueConstraint("assignment_set_id", "task_id", name="uq_assignment_set_item_set_task"),)

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    assignment_set_id: Mapped[int] = mapped_column(
        sa.ForeignKey("assignment_set.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[int] = mapped_column(
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
