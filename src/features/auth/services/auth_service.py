from __future__ import annotations

from dataclasses import dataclass

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ApplicationError, ConflictFailure, UnauthorizedFailure
from src.core.interfaces import UnitOfWork
from src.core.settings import AuthSettings
from src.features.auth.domain.dto import AuthTokensDTO, CurrentUserDTO
from src.features.auth.models import AuthSessionModel
from src.features.auth.repos.user_repo import AuthSessionRepo, UserRepo
from src.features.auth.services.jti_hasher import JtiHasher
from src.features.auth.services.jwt_token_provider import JwtTokenProvider
from src.features.auth.services.password_hasher import PasswordHasher


@dataclass
class AuthService:
    uow: UnitOfWork
    password_hasher: PasswordHasher
    token_provider: JwtTokenProvider
    jti_hasher: JtiHasher
    auth_settings: AuthSettings

    async def login(self, *, email: str, password: str) -> AppResult[AuthTokensDTO]:
        async with self.uow(autocommit=True):
            user_repo = UserRepo(self.uow.session)
            user = await user_repo.get_by_email(email)
            if user is None or not self.password_hasher.verify(password, user.password):
                return Err(UnauthorizedFailure("Invalid email or password"))
            if user.is_blocked:
                return Err(UnauthorizedFailure("Account is disabled"))

            refresh_token, jti, expires_at = self.token_provider.create_refresh_token(
                user_id=user.id,
                role=user.role,
            )
            access_token = self.token_provider.create_access_token(user_id=user.id, role=user.role)

            session_repo = AuthSessionRepo(self.uow.session)
            await session_repo.create(
                AuthSessionModel(
                    user_id=user.id,
                    jti_hash=self.jti_hasher.hash(jti),
                    expires_at=expires_at,
                )
            )

            return Ok(
                AuthTokensDTO(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in=self.auth_settings.access_token_ttl_minutes * 60,
                )
            )

    async def register(self, *, name: str, email: str, password: str) -> AppResult[AuthTokensDTO]:
        # TODO(друг): email verification before register (legacy requires verification code)
        normalized_email = email.lower()
        async with self.uow(autocommit=True):
            user_repo = UserRepo(self.uow.session)
            if await user_repo.get_by_email(normalized_email) is not None:
                return Err(ConflictFailure("User with this email already exists"))

            user = await user_repo.create(
                name=name,
                email=normalized_email,
                password=self.password_hasher.hash(password),
                role="student",
            )

            refresh_token, jti, expires_at = self.token_provider.create_refresh_token(
                user_id=user.id,
                role=user.role,
            )
            access_token = self.token_provider.create_access_token(user_id=user.id, role=user.role)

            await AuthSessionRepo(self.uow.session).create(
                AuthSessionModel(
                    user_id=user.id,
                    jti_hash=self.jti_hasher.hash(jti),
                    expires_at=expires_at,
                )
            )

            return Ok(
                AuthTokensDTO(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in=self.auth_settings.access_token_ttl_minutes * 60,
                )
            )

    async def refresh(self, *, refresh_token: str) -> AppResult[AuthTokensDTO]:
        decode_result = self._decode_refresh_token(refresh_token)
        if decode_result.is_err():
            return decode_result  # type: ignore[return-value]

        payload = decode_result.value
        async with self.uow(autocommit=True):
            jti = str(payload.get("jti") or "")
            user_id = int(str(payload.get("sub") or "0"))
            role = str(payload.get("role") or "student")

            session_repo = AuthSessionRepo(self.uow.session)
            session = await session_repo.get_active_by_jti(self.jti_hasher.hash(jti))
            if session is None or session.user_id != user_id:
                return Err(UnauthorizedFailure("Refresh session is invalid"))

            user_repo = UserRepo(self.uow.session)
            user = await user_repo.get_by_id(user_id)
            if user is None or user.is_blocked:
                return Err(UnauthorizedFailure("Account is disabled"))

            await session_repo.revoke(session)

            new_refresh, new_jti, expires_at = self.token_provider.create_refresh_token(
                user_id=user.id,
                role=role,
            )
            access_token = self.token_provider.create_access_token(user_id=user.id, role=user.role)
            await session_repo.create(
                AuthSessionModel(
                    user_id=user.id,
                    jti_hash=self.jti_hasher.hash(new_jti),
                    expires_at=expires_at,
                )
            )

            return Ok(
                AuthTokensDTO(
                    access_token=access_token,
                    refresh_token=new_refresh,
                    expires_in=self.auth_settings.access_token_ttl_minutes * 60,
                )
            )

    async def logout(self, *, refresh_token: str) -> AppResult[None]:
        decode_result = self._decode_refresh_token(refresh_token)
        if decode_result.is_err():
            return decode_result  # type: ignore[return-value]

        payload = decode_result.value
        async with self.uow(autocommit=True):
            jti = str(payload.get("jti") or "")
            if not jti:
                return Err(UnauthorizedFailure("Refresh session is invalid"))

            session_repo = AuthSessionRepo(self.uow.session)
            session = await session_repo.get_active_by_jti(self.jti_hasher.hash(jti))
            if session is not None:
                await session_repo.revoke(session)

            return Ok(None)

    async def get_current_user(self, user_id: int) -> AppResult[CurrentUserDTO]:
        async with self.uow(autocommit=False):
            user = await UserRepo(self.uow.session).get_by_id(user_id)
            if user is None or user.is_blocked:
                return Err(UnauthorizedFailure("Account is disabled"))
            return Ok(
                CurrentUserDTO(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    role=user.role,
                )
            )

    def _decode_refresh_token(self, refresh_token: str) -> AppResult[dict[str, object]]:
        try:
            return Ok(self.token_provider.decode_refresh_token(refresh_token))
        except ApplicationError as exc:
            return Err(exc.failure)
