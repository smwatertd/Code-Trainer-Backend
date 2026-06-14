from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthTokensDTO:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"


@dataclass(frozen=True)
class CurrentUserDTO:
    id: int
    email: str
    name: str
    role: str
