from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.auth.models import AuthSessionModel, UserModel


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.email == email.lower(),
            UserModel.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role: str = "student",
    ) -> UserModel:
        user = UserModel(
            name=name,
            email=email.lower(),
            password=password,
            role=role,
        )
        self._session.add(user)
        await self._session.flush()
        return user


class AuthSessionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, session: AuthSessionModel) -> AuthSessionModel:
        self._session.add(session)
        await self._session.flush()
        return session

    async def get_active_by_jti(self, jti_hash: str) -> AuthSessionModel | None:
        stmt = select(AuthSessionModel).where(
            AuthSessionModel.jti_hash == jti_hash,
            AuthSessionModel.revoked_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, session: AuthSessionModel) -> None:
        from src.shared.database.base import utc_now

        session.revoked_at = utc_now()
        await self._session.flush()
