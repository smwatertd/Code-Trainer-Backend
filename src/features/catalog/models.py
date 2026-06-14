from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database.base import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String, default="")
    difficulty: Mapped[str] = mapped_column(String(32), default="easy")
    task_type: Mapped[str] = mapped_column(String(64))
    visibility: Mapped[str] = mapped_column(String(32), default="public")
    workflow_status: Mapped[str] = mapped_column(String(32), default="active")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
