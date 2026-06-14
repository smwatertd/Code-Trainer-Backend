from __future__ import annotations

import pytest

from src.core.settings import GuestSettings
from src.features.demo.services.guest_rate_limiter import (
    GuestRateLimitError,
    MemoryGuestRateLimiter,
    RedisGuestRateLimiter,
    create_guest_rate_limiter,
)


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._counters: dict[str, int] = {}
        self._ttl: dict[str, int] = {}

    def incr(self, key: str) -> int:
        self._counters[key] = int(self._counters.get(key, 0)) + 1
        return self._counters[key]

    def expire(self, key: str, seconds: int) -> bool:
        self._ttl[key] = seconds
        return True

    def get(self, key: str) -> str | None:
        if key in self._counters:
            return str(self._counters[key])
        return self._data.get(key)

    def decr(self, key: str) -> int:
        self._counters[key] = max(0, int(self._counters.get(key, 0)) - 1)
        return self._counters[key]


def test_memory_guest_rate_limiter__blocks_concurrent_checks() -> None:
    limiter = MemoryGuestRateLimiter(max_checks_per_minute=8, max_concurrent_checks=1)
    limiter.on_job_queued("127.0.0.1")

    with pytest.raises(GuestRateLimitError):
        limiter.check_submit("127.0.0.1")


def test_redis_guest_rate_limiter__tracks_rate_and_active() -> None:
    limiter = RedisGuestRateLimiter(
        guest_settings=GuestSettings(max_checks_per_minute=8, max_concurrent_checks=1),
        redis_url="redis://localhost:6379/0",
        _client=_FakeRedis(),  # type: ignore[arg-type]
    )

    limiter.check_submit("10.0.0.1")
    limiter.on_job_queued("10.0.0.1")

    with pytest.raises(GuestRateLimitError):
        limiter.check_submit("10.0.0.1")

    limiter.on_job_finished("10.0.0.1")
    limiter.check_submit("10.0.0.1")


def test_create_guest_rate_limiter__uses_memory_by_default() -> None:
    limiter = create_guest_rate_limiter(
        guest_settings=GuestSettings(),
        redis_url="redis://localhost:6379/0",
        use_redis=False,
    )

    assert isinstance(limiter, MemoryGuestRateLimiter)


def test_create_guest_rate_limiter__uses_redis_when_enabled() -> None:
    limiter = create_guest_rate_limiter(
        guest_settings=GuestSettings(),
        redis_url="redis://localhost:6379/0",
        use_redis=True,
    )

    assert isinstance(limiter, RedisGuestRateLimiter)
