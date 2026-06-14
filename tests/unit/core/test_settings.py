from __future__ import annotations

from src.core.settings import AppSettings, CorsSettings, ExecutionSettings, GuestSettings, RedisSettings


def test_cors_settings__parses_comma_separated_origins() -> None:
    settings = CorsSettings(origins="http://a.test, http://b.test")

    assert settings.origin_list() == ["http://a.test", "http://b.test"]


def test_cors_settings__falls_back_to_defaults_when_empty() -> None:
    settings = CorsSettings(origins="  ,  , ")

    assert "http://localhost:5173" in settings.origin_list()


def test_guest_settings__defaults_enable_demo_mode() -> None:
    settings = GuestSettings()

    assert settings.enabled is True
    assert settings.max_checks_per_minute == 8
    assert settings.max_concurrent_checks == 1


def test_execution_settings__defaults_to_in_memory_store() -> None:
    settings = ExecutionSettings()

    assert settings.use_redis_store is False
    assert settings.poll_timeout_seconds == 5
    assert settings.queue_default == "execution:queue:default"


def test_redis_settings__default_url() -> None:
    assert RedisSettings().url == "redis://localhost:6379/0"


def test_app_settings__loads_nested_db_and_redis() -> None:
    settings = AppSettings(
        db={"name": "test_db", "host": "db.local", "port": 5433},  # type: ignore[arg-type]
        redis={"url": "redis://cache:6379/1"},
        cors={"origins": "http://frontend.test"},
        guest={"enabled": False},
    )

    assert settings.db.name == "test_db"
    assert settings.db.dsn == "postgresql+asyncpg://postgres:postgres@db.local:5433/test_db"
    assert settings.redis.url == "redis://cache:6379/1"
    assert settings.cors.origin_list() == ["http://frontend.test"]
    assert settings.guest.enabled is False
