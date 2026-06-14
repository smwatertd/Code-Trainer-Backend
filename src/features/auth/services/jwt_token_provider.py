from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt import ExpiredSignatureError
from jwt import InvalidTokenError as PyJwtInvalidTokenError

from src.core.either.failures import ApplicationError, UnauthorizedFailure
from src.core.settings import AuthSettings


class JwtTokenProvider:
    def __init__(self, settings: AuthSettings) -> None:
        self._settings = settings

    def create_access_token(self, *, user_id: int, role: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=self._settings.access_token_ttl_minutes),
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
        }
        return jwt.encode(payload, self._settings.secret_key, algorithm="HS256")

    def create_refresh_token(self, *, user_id: int, role: str) -> tuple[str, str, datetime]:
        now = datetime.now(UTC)
        jti = str(uuid4())
        expires_at = now + timedelta(days=self._settings.refresh_token_ttl_days)
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "refresh",
            "jti": jti,
            "iat": now,
            "nbf": now,
            "exp": expires_at,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
        }
        token = jwt.encode(payload, self._settings.secret_key, algorithm="HS256")
        return token, jti, expires_at

    def decode_access_token(self, token: str) -> dict[str, object]:
        return self._decode(token, expected_type="access")

    def decode_refresh_token(self, token: str) -> dict[str, object]:
        return self._decode(token, expected_type="refresh")

    def _decode(self, token: str, *, expected_type: str) -> dict[str, object]:
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=["HS256"],
                issuer=self._settings.issuer,
                audience=self._settings.audience,
            )
        except ExpiredSignatureError as exc:
            raise ApplicationError(UnauthorizedFailure("Token is expired")) from exc
        except PyJwtInvalidTokenError as exc:
            raise ApplicationError(UnauthorizedFailure("Token is invalid")) from exc

        if payload.get("type") != expected_type:
            raise ApplicationError(UnauthorizedFailure("Invalid token type"))
        return payload
