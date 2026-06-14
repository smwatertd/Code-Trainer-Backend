from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.containers import Container
from src.features.auth.commands import (
    GetCurrentUserCommand,
    LoginCommand,
    LogoutCommand,
    RefreshTokensCommand,
    RegisterCommand,
)
from src.features.auth.dependencies import AuthenticatedUser, get_authenticated_user
from src.features.auth.schemas import AuthResponse, CurrentUserResponse, LoginRequest, RefreshRequest, RegisterRequest
from src.features.auth.usecases import (
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokensUseCase,
    RegisterUseCase,
)
from src.shared.handlers.http_handlers import unwrap_ok_or_http_exc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
@inject
async def login(
    body: LoginRequest,
    use_case: LoginUseCase = Depends(Provide[Container.auth.login_use_case]),
) -> AuthResponse:
    result = await use_case.execute(LoginCommand(email=str(body.email), password=body.password))
    tokens = unwrap_ok_or_http_exc(result)
    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
@inject
async def register(
    body: RegisterRequest,
    use_case: RegisterUseCase = Depends(Provide[Container.auth.register_use_case]),
) -> AuthResponse:
    result = await use_case.execute(
        RegisterCommand(name=body.name, email=str(body.email), password=body.password),
    )
    tokens = unwrap_ok_or_http_exc(result)
    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post("/refresh", response_model=AuthResponse)
@inject
async def refresh_tokens(
    body: RefreshRequest,
    use_case: RefreshTokensUseCase = Depends(Provide[Container.auth.refresh_tokens_use_case]),
) -> AuthResponse:
    result = await use_case.execute(RefreshTokensCommand(refresh_token=body.refresh_token))
    tokens = unwrap_ok_or_http_exc(result)
    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post("/logout", status_code=204)
@inject
async def logout(
    body: RefreshRequest,
    use_case: LogoutUseCase = Depends(Provide[Container.auth.logout_use_case]),
) -> None:
    result = await use_case.execute(LogoutCommand(refresh_token=body.refresh_token))
    unwrap_ok_or_http_exc(result)


@router.get("/me", response_model=CurrentUserResponse)
@inject
async def get_me(
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    use_case: GetCurrentUserUseCase = Depends(Provide[Container.auth.get_current_user_use_case]),
) -> CurrentUserResponse:
    result = await use_case.execute(GetCurrentUserCommand(user_id=current_user.user_id))
    user = unwrap_ok_or_http_exc(result)
    return CurrentUserResponse(id=user.id, email=user.email, name=user.name, role=user.role)
