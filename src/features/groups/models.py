from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database.base import Base, utc_now

group_member_table = sa.Table(
    "group_member",
    Base.metadata,
    sa.Column(
        "group_id",
        sa.Integer,
        sa.ForeignKey("study_group.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "student_id",
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
)


class StudyGroupModel(Base):
    __tablename__ = "study_group"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    invitation_codes: Mapped[list[InvitationCodeModel]] = relationship(
        "InvitationCodeModel",
        back_populates="group",
    )


class InvitationCodeModel(Base):
    __tablename__ = "group_invitation_code"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(sa.String(32), nullable=False, unique=True, index=True)
    group_id: Mapped[int] = mapped_column(
        sa.ForeignKey("study_group.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    max_uses: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    use_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    group: Mapped[StudyGroupModel] = relationship("StudyGroupModel", back_populates="invitation_codes")
