from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import AuthSettings
from src.features.auth.commands import LoginCommand
from src.features.auth.models import UserModel
from src.features.auth.services.auth_service import AuthService
from src.features.auth.services.jti_hasher import JtiHasher
from src.features.auth.services.jwt_token_provider import JwtTokenProvider
from src.features.auth.services.password_hasher import PasswordHasher
from src.features.auth.usecases import LoginUseCase
from src.shared.database.uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_login__returns_tokens_for_seeded_user(
    session: AsyncSession,
    session_factory: object,
) -> None:
    hasher = PasswordHasher()
    user = UserModel(
        name="Test User",
        email="student@test.local",
        password=hasher.hash("password123"),
        role="student",
    )
    session.add(user)
    await session.flush()

    uow = SqlAlchemyUnitOfWork(session_factory)  # type: ignore[arg-type]
    settings = AuthSettings(secret_key="integration-test-jwt-secret-key-32")
    service = AuthService(
        uow=uow,
        password_hasher=hasher,
        token_provider=JwtTokenProvider(settings),
        jti_hasher=JtiHasher(settings.secret_key),
        auth_settings=settings,
    )
    use_case = LoginUseCase(auth_service=service)

    result = await use_case.execute(LoginCommand(email="student@test.local", password="password123"))

    assert result.is_ok()
    assert result.value.access_token
    assert result.value.refresh_token
