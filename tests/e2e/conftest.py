from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import uuid4

import httpx
import pytest_asyncio
from dependency_injector import providers
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.core.containers import Container
from src.core.rest import create_app
from src.core.settings import AppSettings, GuestSettings
from src.features.auth.models import AuthSessionModel, UserModel
from src.features.auth.services.jti_hasher import JtiHasher
from src.features.auth.services.jwt_token_provider import JwtTokenProvider
from src.features.auth.services.password_hasher import PasswordHasher
from src.features.demo.services.guest_rate_limiter import GuestRateLimiter
from src.features.submissions.models import (
    SubmissionLintErrorModel,
    SubmissionModel,
    SubmissionPatternErrorModel,
)
from src.shared.database.base import configure_search_path
from src.shared.database.uow import SqlAlchemyUnitOfWork
from src.shared.execution.services.composite_job_processor import CompositeJobProcessor
from src.shared.execution.services.execution_rate_limiter import MemoryExecutionRateLimiter
from src.shared.execution.services.execution_service import ExecutionService
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.stores.memory_job_store import MemoryJobStore

E2E_HTTP_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


@dataclass(frozen=True)
class E2EAuthUser:
    email: str
    password: str
    user_id: int
    submission_id: int
    access_token: str | None = None
    refresh_token: str | None = None


async def _seed_blocked_user_tokens(
    *,
    session: AsyncSession,
    settings: AppSettings,
    user: UserModel,
) -> tuple[str, str]:
    token_provider = JwtTokenProvider(settings.auth)
    jti_hasher = JtiHasher(settings.auth.secret_key)
    access_token = token_provider.create_access_token(user_id=user.id, role=user.role)
    refresh_token, jti, expires_at = token_provider.create_refresh_token(
        user_id=user.id,
        role=user.role,
    )
    session.add(
        AuthSessionModel(
            user_id=user.id,
            jti_hash=jti_hasher.hash(jti),
            expires_at=expires_at,
        ),
    )
    await session.flush()
    return access_token, refresh_token


async def _build_client(
    settings: AppSettings,
    *,
    auto_process: bool = True,
    guest_rate_limiter_factory: type[GuestRateLimiter] = GuestRateLimiter,
    guest_rate_limiter_kwargs: dict[str, int] | None = None,
    seed_auth_data: bool = False,
    user_role: str = "student",
    user_is_blocked: bool = False,
    execution_rate_limiter: MemoryExecutionRateLimiter | None = None,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser | None], None]:
    engine = create_async_engine(settings.db.dsn, echo=settings.db.echo)
    configure_search_path(engine, settings.db.db_schema)

    auth_user: E2EAuthUser | None = None
    limiter_kwargs = guest_rate_limiter_kwargs or {}
    seed_session: AsyncSession | None = None

    async with engine.connect() as connection:
        async with connection.begin():
            session_factory = async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )

            if seed_auth_data:
                hasher = PasswordHasher()
                email = f"e2e-student-{uuid4().hex[:8]}@example.com"
                seed_session = session_factory()
                user = UserModel(
                    name="E2E Student",
                    email=email,
                    password=hasher.hash("password123"),
                    role=user_role,
                    is_blocked=user_is_blocked,
                )
                seed_session.add(user)
                await seed_session.flush()

                submission = SubmissionModel(
                    user_id=user.id,
                    task_id=2,
                    language="python",
                    code="print('b')\nprint('a')",
                    status="success",
                    success=True,
                )
                submission.linter_errors = [
                    SubmissionLintErrorModel(error_type="COMPILER", text="none"),
                ]
                submission.pattern_errors = [
                    SubmissionPatternErrorModel(error_type="PATTERN", text="ok"),
                ]
                seed_session.add(submission)
                await seed_session.flush()

                access_token: str | None = None
                refresh_token: str | None = None
                if user_is_blocked:
                    access_token, refresh_token = await _seed_blocked_user_tokens(
                        session=seed_session,
                        settings=settings,
                        user=user,
                    )

                auth_user = E2EAuthUser(
                    email=user.email,
                    password="password123",
                    user_id=user.id,
                    submission_id=submission.id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                )

            container = Container()
            container.config.override(providers.Object(settings))
            container.db.uow.override(
                providers.Factory(
                    SqlAlchemyUnitOfWork,
                    session_factory=session_factory,
                )
            )

            job_store = MemoryJobStore()
            processor = CompositeJobProcessor(guest_processor=GuestJobProcessor())
            execution_service = ExecutionService(
                store=job_store,
                auto_process=auto_process,
                processor=processor,
            )
            container.execution.job_store.override(providers.Object(job_store))
            container.execution.guest_job_processor.override(providers.Object(processor))
            container.execution.execution_service.override(providers.Object(execution_service))
            container.demo.guest_rate_limiter.override(providers.Object(guest_rate_limiter_factory(**limiter_kwargs)))
            if execution_rate_limiter is not None:
                container.submissions.execution_rate_limiter.override(providers.Object(execution_rate_limiter))

            application = create_app(container=container)
            async with application.router.lifespan_context(application):
                async with AsyncClient(
                    transport=ASGITransport(app=application),
                    base_url="http://test",
                    timeout=E2E_HTTP_TIMEOUT,
                ) as http_client:
                    yield http_client, auth_user

            if seed_session is not None:
                await seed_session.close()

    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(settings: AppSettings, engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    del engine
    async for http_client, _ in _build_client(settings):
        yield http_client


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def guest_disabled_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    del engine
    app_settings = settings.model_copy(update={"guest": GuestSettings(enabled=False)})
    async for http_client, _ in _build_client(app_settings):
        yield http_client


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def strict_guest_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    del engine
    guest_settings = GuestSettings(enabled=True, max_checks_per_minute=1, max_concurrent_checks=1)
    app_settings = settings.model_copy(update={"guest": guest_settings})
    async for http_client, _ in _build_client(
        app_settings,
        auto_process=False,
        guest_rate_limiter_kwargs={"max_checks_per_minute": 1, "max_concurrent_checks": 1},
    ):
        yield http_client


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def concurrent_guest_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    del engine
    async for http_client, _ in _build_client(
        settings,
        auto_process=False,
        guest_rate_limiter_kwargs={"max_checks_per_minute": 100, "max_concurrent_checks": 1},
    ):
        yield http_client


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def dedup_client(settings: AppSettings, engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    del engine
    async for http_client, _ in _build_client(
        settings,
        auto_process=False,
        guest_rate_limiter_kwargs={"max_checks_per_minute": 100, "max_concurrent_checks": 10},
    ):
        yield http_client


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def queued_submissions_client(
    auth_queued_client: tuple[AsyncClient, E2EAuthUser],
) -> AsyncClient:
    return auth_queued_client[0]


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def auth_queued_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    async for http_client, auth_user in _build_client(
        settings,
        seed_auth_data=True,
        auto_process=False,
    ):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def auth_client(
    settings: AppSettings, engine: AsyncEngine
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    async for http_client, auth_user in _build_client(settings, seed_auth_data=True):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def blocked_auth_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    async for http_client, auth_user in _build_client(
        settings,
        seed_auth_data=True,
        user_is_blocked=True,
    ):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def rate_limited_submissions_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    strict_limiter = MemoryExecutionRateLimiter(
        settings=settings.execution.model_copy(
            update={"user_max_per_minute": 1, "user_max_concurrent": 100},
        ),
    )
    async for http_client, auth_user in _build_client(
        settings,
        seed_auth_data=True,
        execution_rate_limiter=strict_limiter,
    ):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def auth_guest_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    async for http_client, auth_user in _build_client(
        settings,
        seed_auth_data=True,
        user_role="guest",
    ):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def teacher_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    async for http_client, auth_user in _build_client(
        settings,
        seed_auth_data=True,
        user_role="teacher",
    ):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def admin_client(
    settings: AppSettings,
    engine: AsyncEngine,
) -> AsyncGenerator[tuple[AsyncClient, E2EAuthUser], None]:
    del engine
    async for http_client, auth_user in _build_client(
        settings,
        seed_auth_data=True,
        user_role="admin",
    ):
        assert auth_user is not None
        yield http_client, auth_user


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def auth_user(auth_client: tuple[AsyncClient, E2EAuthUser]) -> E2EAuthUser:
    return auth_client[1]
