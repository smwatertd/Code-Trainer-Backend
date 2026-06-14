from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.features.auth.models import UserModel


async def set_user_blocked(
    session_factory: async_sessionmaker[AsyncSession],
    user_id: int,
    *,
    blocked: bool = True,
) -> None:
    async with session_factory() as session:
        await session.execute(
            update(UserModel).where(UserModel.id == user_id).values(is_blocked=blocked),
        )
        await session.flush()
