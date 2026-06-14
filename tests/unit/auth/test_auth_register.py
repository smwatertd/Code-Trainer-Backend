from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import ConflictFailure
from src.core.settings import AuthSettings
from src.features.auth.models import UserModel
from src.features.auth.services.auth_service import AuthService
from src.features.auth.services.jti_hasher import JtiHasher
from src.features.auth.services.jwt_token_provider import JwtTokenProvider
from src.features.auth.services.password_hasher import PasswordHasher
from tests.unit.conftest import FakeUoW


@pytest.fixture
def auth_service() -> AuthService:
    settings = AuthSettings(
        secret_key="auth-register-test-jwt-secret-key",
        issuer="code-trainer-test",
        audience="code-trainer-api",
    )
    return AuthService(
        uow=FakeUoW(session=AsyncMock()),
        password_hasher=PasswordHasher(),
        token_provider=JwtTokenProvider(settings),
        jti_hasher=JtiHasher(settings.secret_key),
        auth_settings=settings,
    )


@pytest.mark.asyncio
async def test_auth_service__register_duplicate_email(auth_service: AuthService) -> None:
    existing = UserModel(id=1, name="Taken", email="taken@example.com", password="hash", role="student")

    with patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls:
        user_repo_cls.return_value.get_by_email = AsyncMock(return_value=existing)

        result = await auth_service.register(
            name="New",
            email="taken@example.com",
            password="password123",
        )

    assert isinstance(result, Err)
    assert isinstance(result.error, ConflictFailure)


@pytest.mark.asyncio
async def test_auth_service__register_success(auth_service: AuthService) -> None:
    created = UserModel(id=8, name="Alice", email="alice@example.com", password="hash", role="student")

    with (
        patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls,
        patch("src.features.auth.services.auth_service.AuthSessionRepo") as session_repo_cls,
    ):
        user_repo_cls.return_value.get_by_email = AsyncMock(return_value=None)
        user_repo_cls.return_value.create = AsyncMock(return_value=created)
        session_repo_cls.return_value.create = AsyncMock()

        result = await auth_service.register(
            name="Alice",
            email="alice@example.com",
            password="password123",
        )

    assert isinstance(result, Ok)
    assert result.value.access_token
    assert result.value.refresh_token
