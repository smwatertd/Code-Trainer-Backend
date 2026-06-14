from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.containers import Container
from src.core.either.failures import ApplicationError, UnauthorizedFailure
from src.core.policies.permissions import Permission
from src.features.auth.services.authorization_service import AuthorizationService
from src.features.auth.services.jwt_token_provider import JwtTokenProvider

_bearer = HTTPBearer(auto_error=False)
_authorization_service = AuthorizationService()


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: int
    role: str


def _decode_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None,
    token_provider: JwtTokenProvider,
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApplicationError(UnauthorizedFailure("Authentication required"))

    payload = token_provider.decode_access_token(credentials.credentials)

    return AuthenticatedUser(
        user_id=int(str(payload.get("sub") or "0")),
        role=str(payload.get("role") or "student"),
    )


@inject
def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    token_provider: JwtTokenProvider = Depends(Provide[Container.auth.jwt_token_provider]),
) -> AuthenticatedUser:
    return _decode_authenticated_user(credentials, token_provider)


def require_permission(permission: Permission) -> Callable[..., AuthenticatedUser]:
    @inject
    def _checker(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
        token_provider: JwtTokenProvider = Depends(Provide[Container.auth.jwt_token_provider]),
    ) -> AuthenticatedUser:
        user = _decode_authenticated_user(credentials, token_provider)
        result = _authorization_service.ensure_permission(role=user.role, permission=permission)
        if result.is_err():
            raise ApplicationError(result.error)
        return user

    return _checker
