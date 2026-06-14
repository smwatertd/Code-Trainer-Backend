from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.core.either import Err, Ok
from src.core.either.failures import UnauthorizedFailure
from src.core.settings import AuthSettings
from src.features.auth.models import AuthSessionModel, UserModel
from src.features.auth.services.auth_service import AuthService
from src.features.auth.services.jti_hasher import JtiHasher
from src.features.auth.services.jwt_token_provider import JwtTokenProvider
from src.features.auth.services.password_hasher import PasswordHasher
from tests.unit.conftest import FakeUoW


@pytest.fixture
def auth_settings() -> AuthSettings:
    return AuthSettings(
        secret_key="auth-service-test-jwt-secret-key-32",
        issuer="code-trainer-test",
        audience="code-trainer-api",
        access_token_ttl_minutes=30,
        refresh_token_ttl_days=14,
    )


@pytest.fixture
def auth_service(auth_settings: AuthSettings) -> AuthService:
    return AuthService(
        uow=FakeUoW(session=AsyncMock()),
        password_hasher=PasswordHasher(),
        token_provider=JwtTokenProvider(auth_settings),
        jti_hasher=JtiHasher(auth_settings.secret_key),
        auth_settings=auth_settings,
    )


@pytest.mark.asyncio
async def test_auth_service__login_invalid_credentials(auth_service: AuthService) -> None:
    with patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls:
        user_repo_cls.return_value.get_by_email = AsyncMock(return_value=None)

        result = await auth_service.login(email="missing@test.local", password="wrong")

    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedFailure)


@pytest.mark.asyncio
async def test_auth_service__login_blocked_user(auth_service: AuthService) -> None:
    hasher = PasswordHasher()
    user = UserModel(
        id=1,
        name="Blocked",
        email="blocked@test.local",
        password=hasher.hash("secret"),
        role="student",
        is_blocked=True,
    )

    with patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls:
        user_repo_cls.return_value.get_by_email = AsyncMock(return_value=user)

        result = await auth_service.login(email=user.email, password="secret")

    assert isinstance(result, Err)
    assert result.error.message == "Account is disabled"


@pytest.mark.asyncio
async def test_auth_service__login_success_creates_session(auth_service: AuthService) -> None:
    hasher = PasswordHasher()
    user = UserModel(
        id=5,
        name="Student",
        email="student@test.local",
        password=hasher.hash("secret"),
        role="student",
    )
    session_create = AsyncMock()

    with (
        patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls,
        patch("src.features.auth.services.auth_service.AuthSessionRepo") as session_repo_cls,
    ):
        user_repo_cls.return_value.get_by_email = AsyncMock(return_value=user)
        session_repo_cls.return_value.create = session_create

        result = await auth_service.login(email=user.email, password="secret")

    assert isinstance(result, Ok)
    assert result.value.access_token
    assert result.value.refresh_token
    assert result.value.expires_in == 30 * 60
    session_create.assert_awaited_once()
    created_session: AuthSessionModel = session_create.await_args.args[0]
    assert created_session.user_id == user.id
    assert created_session.jti_hash != ""
    assert len(created_session.jti_hash) == 64


@pytest.mark.asyncio
async def test_auth_service__refresh_invalid_token(auth_service: AuthService) -> None:
    result = await auth_service.refresh(refresh_token="not-a-jwt")

    assert result.is_err()
    assert isinstance(result.error, UnauthorizedFailure)


@pytest.mark.asyncio
async def test_auth_service__refresh_revokes_old_session(auth_service: AuthService) -> None:
    hasher = PasswordHasher()
    user = UserModel(
        id=9,
        name="Student",
        email="refresh@test.local",
        password=hasher.hash("secret"),
        role="student",
    )
    refresh, jti, expires_at = auth_service.token_provider.create_refresh_token(
        user_id=user.id,
        role=user.role,
    )
    session = AuthSessionModel(
        user_id=user.id,
        jti_hash=auth_service.jti_hasher.hash(jti),
        expires_at=expires_at,
    )
    revoke = AsyncMock()
    create = AsyncMock()

    with (
        patch("src.features.auth.services.auth_service.AuthSessionRepo") as session_repo_cls,
        patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls,
    ):
        session_repo_cls.return_value.get_active_by_jti = AsyncMock(return_value=session)
        session_repo_cls.return_value.revoke = revoke
        session_repo_cls.return_value.create = create
        user_repo_cls.return_value.get_by_id = AsyncMock(return_value=user)

        result = await auth_service.refresh(refresh_token=refresh)

    assert isinstance(result, Ok)
    revoke.assert_awaited_once_with(session)
    create.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service__logout_revokes_active_session(auth_service: AuthService) -> None:
    user = UserModel(id=2, name="Bob", email="bob@test.local", password="hash", role="student")
    refresh, jti, expires_at = auth_service.token_provider.create_refresh_token(
        user_id=user.id,
        role=user.role,
    )
    session = AuthSessionModel(
        user_id=user.id,
        jti_hash=auth_service.jti_hasher.hash(jti),
        expires_at=expires_at,
    )
    revoke = AsyncMock()

    with patch("src.features.auth.services.auth_service.AuthSessionRepo") as session_repo_cls:
        session_repo_cls.return_value.get_active_by_jti = AsyncMock(return_value=session)
        session_repo_cls.return_value.revoke = revoke

        result = await auth_service.logout(refresh_token=refresh)

    assert isinstance(result, Ok)
    revoke.assert_awaited_once_with(session)


@pytest.mark.asyncio
async def test_auth_service__logout_is_idempotent_when_session_missing(auth_service: AuthService) -> None:
    user = UserModel(id=2, name="Bob", email="bob@test.local", password="hash", role="student")
    refresh, _, _ = auth_service.token_provider.create_refresh_token(user_id=user.id, role=user.role)

    with patch("src.features.auth.services.auth_service.AuthSessionRepo") as session_repo_cls:
        session_repo_cls.return_value.get_active_by_jti = AsyncMock(return_value=None)

        result = await auth_service.logout(refresh_token=refresh)

    assert isinstance(result, Ok)


@pytest.mark.asyncio
async def test_auth_service__get_current_user_not_found(auth_service: AuthService) -> None:
    with patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls:
        user_repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        result = await auth_service.get_current_user(404)

    assert isinstance(result, Err)
    assert result.error.message == "Account is disabled"


@pytest.mark.asyncio
async def test_auth_service__get_current_user_success(auth_service: AuthService) -> None:
    user = UserModel(
        id=3,
        name="Alice",
        email="alice@test.local",
        password="hash",
        role="teacher",
    )

    with patch("src.features.auth.services.auth_service.UserRepo") as user_repo_cls:
        user_repo_cls.return_value.get_by_id = AsyncMock(return_value=user)

        result = await auth_service.get_current_user(user.id)

    assert isinstance(result, Ok)
    assert result.value.email == user.email
    assert result.value.role == "teacher"
