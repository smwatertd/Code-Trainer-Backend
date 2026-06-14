from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult
from src.features.auth.commands import (
    GetCurrentUserCommand,
    LoginCommand,
    LogoutCommand,
    RefreshTokensCommand,
    RegisterCommand,
)
from src.features.auth.domain.dto import AuthTokensDTO, CurrentUserDTO
from src.features.auth.services.auth_service import AuthService


@dataclass
class LoginUseCase:
    auth_service: AuthService

    async def execute(self, command: LoginCommand) -> AppResult[AuthTokensDTO]:
        return await self.auth_service.login(email=command.email, password=command.password)


@dataclass
class RegisterUseCase:
    auth_service: AuthService

    async def execute(self, command: RegisterCommand) -> AppResult[AuthTokensDTO]:
        return await self.auth_service.register(
            name=command.name,
            email=command.email,
            password=command.password,
        )


@dataclass
class RefreshTokensUseCase:
    auth_service: AuthService

    async def execute(self, command: RefreshTokensCommand) -> AppResult[AuthTokensDTO]:
        return await self.auth_service.refresh(refresh_token=command.refresh_token)


@dataclass
class LogoutUseCase:
    auth_service: AuthService

    async def execute(self, command: LogoutCommand) -> AppResult[None]:
        return await self.auth_service.logout(refresh_token=command.refresh_token)


@dataclass
class GetCurrentUserUseCase:
    auth_service: AuthService

    async def execute(self, command: GetCurrentUserCommand) -> AppResult[CurrentUserDTO]:
        return await self.auth_service.get_current_user(command.user_id)
