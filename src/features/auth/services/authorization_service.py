from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ForbiddenFailure
from src.core.policies.permissions import Permission, can, can_any


@dataclass(frozen=True)
class AuthorizationService:
    def ensure_permission(self, *, role: str, permission: Permission) -> AppResult[None]:
        if not can(role, permission):
            return Err(ForbiddenFailure("Not enough permissions"))
        return Ok(None)

    def ensure_any_permission(self, *, role: str, permissions: tuple[Permission, ...]) -> AppResult[None]:
        if not can_any(role, *permissions):
            return Err(ForbiddenFailure("Not enough permissions"))
        return Ok(None)
