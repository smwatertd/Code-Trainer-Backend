from __future__ import annotations

from dependency_injector import containers, providers

from src.core.logger import LoguruLogger
from src.core.settings import AppSettings
from src.features.auth.services.auth_service import AuthService
from src.features.auth.services.jti_hasher import JtiHasher
from src.features.auth.services.jwt_token_provider import JwtTokenProvider
from src.features.auth.services.password_hasher import PasswordHasher
from src.features.auth.usecases import (
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokensUseCase,
    RegisterUseCase,
)


class AuthContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)
    uow = providers.Dependency()

    logger = providers.Singleton(LoguruLogger, name="auth")

    password_hasher = providers.Singleton(PasswordHasher)

    jwt_token_provider = providers.Singleton(
        JwtTokenProvider,
        settings=config.provided.auth,
    )

    jti_hasher = providers.Singleton(
        JtiHasher,
        secret_key=config.provided.auth.secret_key,
    )

    auth_service = providers.Factory(
        AuthService,
        uow=uow,
        password_hasher=password_hasher,
        token_provider=jwt_token_provider,
        jti_hasher=jti_hasher,
        auth_settings=config.provided.auth,
    )

    login_use_case = providers.Factory(LoginUseCase, auth_service=auth_service)
    register_use_case = providers.Factory(RegisterUseCase, auth_service=auth_service)
    refresh_tokens_use_case = providers.Factory(RefreshTokensUseCase, auth_service=auth_service)
    logout_use_case = providers.Factory(LogoutUseCase, auth_service=auth_service)
    get_current_user_use_case = providers.Factory(GetCurrentUserUseCase, auth_service=auth_service)
