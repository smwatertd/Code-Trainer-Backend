from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]

_DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
)


class DBSettings(BaseModel):
    name: str = "code_trainer"
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    dialect: str = "postgresql+asyncpg"
    pool_size: int = 2
    max_overflow: int = 4
    echo: bool = False
    db_schema: str = "public"

    @property
    def dsn(self) -> str:
        return f"{self.dialect}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    url: str = "redis://localhost:6379/0"


class CorsSettings(BaseModel):
    origins: str = ",".join(_DEFAULT_CORS_ORIGINS)

    def origin_list(self) -> list[str]:
        parsed = [item.strip() for item in self.origins.split(",") if item.strip()]
        return parsed or list(_DEFAULT_CORS_ORIGINS)


class GuestSettings(BaseModel):
    enabled: bool = True
    max_checks_per_minute: int = 8
    max_concurrent_checks: int = 1


class AuthSettings(BaseModel):
    secret_key: str = "change-me-in-production-min-32-chars"
    issuer: str = "code-trainer"
    audience: str = "code-trainer-api"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30


class ExecutionSettings(BaseModel):
    use_redis_store: bool = False
    job_ttl_seconds: int = 3600
    poll_timeout_seconds: int = 5
    queue_prefix: str = "execution:queue"
    queue_default: str = "execution:queue:default"
    job_key_prefix: str = "execution:job:"
    result_key_prefix: str = "execution:result:"
    dedup_key_prefix: str = "execution:dedup:"
    global_depth_key: str = "execution:metrics:queue_depth"
    user_lock_prefix: str = "execution:user:"
    user_rate_prefix: str = "execution:rate:"
    global_max_queue: int = 500
    user_max_per_minute: int = 10
    user_max_concurrent: int = 2
    rate_limit_window_seconds: int = 60
    prefer_docker_runner: bool = True
    runner_timeout_seconds: int = 5
    use_warm_runners: bool = True
    warm_runner_recycle_after: int = 500
    execution_output_max_bytes: int = 262_144
    cold_run_cpus: str = "0.5"
    cold_run_memory: str = "256m"
    cold_run_pids_limit: int = 64


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    title: str = "Code Trainer API"
    version: str = "0.1.0"
    debug: bool = False
    docs_url: str = "/docs"

    languages_dir: Path = Field(default=_BACKEND_ROOT / "languages")
    curriculum_dir: Path = Field(default=_BACKEND_ROOT / "resources" / "curriculum")
    db: DBSettings = Field(default_factory=DBSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
    guest: GuestSettings = Field(default_factory=GuestSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
