from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from src.core.either.failures import ApplicationError, UnauthorizedFailure
from src.core.settings import AuthSettings
from src.features.auth.services.jwt_token_provider import JwtTokenProvider


@pytest.fixture
def auth_settings() -> AuthSettings:
    return AuthSettings(
        secret_key="unit-test-jwt-secret-key-32-bytes-min",
        issuer="code-trainer-test",
        audience="code-trainer-api",
        access_token_ttl_minutes=15,
        refresh_token_ttl_days=7,
    )


@pytest.fixture
def token_provider(auth_settings: AuthSettings) -> JwtTokenProvider:
    return JwtTokenProvider(auth_settings)


def test_jwt_token_provider__access_roundtrip(token_provider: JwtTokenProvider) -> None:
    token = token_provider.create_access_token(user_id=42, role="student")
    payload = token_provider.decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "student"
    assert payload["type"] == "access"


def test_jwt_token_provider__refresh_roundtrip(token_provider: JwtTokenProvider) -> None:
    refresh, jti, expires_at = token_provider.create_refresh_token(user_id=7, role="teacher")

    assert jti
    assert expires_at > datetime.now(UTC)

    payload = token_provider.decode_refresh_token(refresh)
    assert payload["sub"] == "7"
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"


def test_jwt_token_provider__rejects_access_as_refresh(token_provider: JwtTokenProvider) -> None:
    access = token_provider.create_access_token(user_id=1, role="student")

    with pytest.raises(ApplicationError) as exc_info:
        token_provider.decode_refresh_token(access)

    assert isinstance(exc_info.value.failure, UnauthorizedFailure)


def test_jwt_token_provider__rejects_expired_token(token_provider: JwtTokenProvider) -> None:
    now = datetime.now(UTC)
    payload = {
        "sub": "1",
        "role": "student",
        "type": "access",
        "iat": now - timedelta(hours=2),
        "nbf": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "iss": token_provider._settings.issuer,
        "aud": token_provider._settings.audience,
    }
    expired = jwt.encode(payload, token_provider._settings.secret_key, algorithm="HS256")

    with pytest.raises(ApplicationError) as exc_info:
        token_provider.decode_access_token(expired)

    assert isinstance(exc_info.value.failure, UnauthorizedFailure)


def test_jwt_token_provider__rejects_invalid_signature(token_provider: JwtTokenProvider) -> None:
    token = token_provider.create_access_token(user_id=1, role="student")
    tampered = f"{token}invalid"

    with pytest.raises(ApplicationError) as exc_info:
        token_provider.decode_access_token(tampered)

    assert isinstance(exc_info.value.failure, UnauthorizedFailure)
