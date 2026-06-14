from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol

import redis

from src.core.settings import GuestSettings


class GuestRateLimitError(Exception):
    pass


class GuestRateLimiterProtocol(Protocol):
    @staticmethod
    def guest_user_id(client_ip: str) -> str: ...

    def check_submit(self, client_ip: str) -> None: ...

    def on_job_queued(self, client_ip: str) -> None: ...

    def on_job_finished(self, client_ip: str) -> None: ...


_GUEST_RATE_PREFIX = "guest:rate:"
_GUEST_ACTIVE_PREFIX = "guest:active:"
_WINDOW_SECONDS = 60


@dataclass
class MemoryGuestRateLimiter:
    max_checks_per_minute: int = 8
    max_concurrent_checks: int = 1
    window_seconds: int = 60
    _rate_counts: dict[str, tuple[int, datetime]] = field(default_factory=dict)
    _active_counts: dict[str, int] = field(default_factory=dict)

    @staticmethod
    def guest_user_id(client_ip: str) -> str:
        digest = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:16]
        return f"guest:{digest}"

    def check_submit(self, client_ip: str) -> None:
        now = datetime.now(UTC)
        rate_key = client_ip
        count, expires_at = self._rate_counts.get(rate_key, (0, now))
        if now >= expires_at:
            count = 0
            expires_at = now + timedelta(seconds=self.window_seconds)
        count += 1
        self._rate_counts[rate_key] = (count, expires_at)
        if count > self.max_checks_per_minute:
            raise GuestRateLimitError("Too many guest checks per minute.")

        active = self._active_counts.get(rate_key, 0)
        if active >= self.max_concurrent_checks:
            raise GuestRateLimitError("Guest check already in progress.")

    def on_job_queued(self, client_ip: str) -> None:
        self._active_counts[client_ip] = self._active_counts.get(client_ip, 0) + 1

    def on_job_finished(self, client_ip: str) -> None:
        current = self._active_counts.get(client_ip, 0)
        if current > 0:
            self._active_counts[client_ip] = current - 1


@dataclass
class RedisGuestRateLimiter:
    guest_settings: GuestSettings
    redis_url: str
    window_seconds: int = _WINDOW_SECONDS
    _client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    @staticmethod
    def guest_user_id(client_ip: str) -> str:
        digest = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:16]
        return f"guest:{digest}"

    def check_submit(self, client_ip: str) -> None:
        rate_key = f"{_GUEST_RATE_PREFIX}{client_ip}"
        count = int(self.client.incr(rate_key))
        if count == 1:
            self.client.expire(rate_key, self.window_seconds)
        if count > self.guest_settings.max_checks_per_minute:
            raise GuestRateLimitError("Too many guest checks per minute.")

        active_key = f"{_GUEST_ACTIVE_PREFIX}{client_ip}"
        active = int(self.client.get(active_key) or 0)
        if active >= self.guest_settings.max_concurrent_checks:
            raise GuestRateLimitError("Guest check already in progress.")

    def on_job_queued(self, client_ip: str) -> None:
        active_key = f"{_GUEST_ACTIVE_PREFIX}{client_ip}"
        count = int(self.client.incr(active_key))
        if count == 1:
            self.client.expire(active_key, self.window_seconds * 10)

    def on_job_finished(self, client_ip: str) -> None:
        active_key = f"{_GUEST_ACTIVE_PREFIX}{client_ip}"
        current = int(self.client.get(active_key) or 0)
        if current > 0:
            self.client.decr(active_key)


def create_guest_rate_limiter(
    *,
    guest_settings: GuestSettings,
    redis_url: str,
    use_redis: bool,
) -> MemoryGuestRateLimiter | RedisGuestRateLimiter:
    if use_redis and redis_url:
        return RedisGuestRateLimiter(guest_settings=guest_settings, redis_url=redis_url)
    return MemoryGuestRateLimiter(
        max_checks_per_minute=guest_settings.max_checks_per_minute,
        max_concurrent_checks=guest_settings.max_concurrent_checks,
    )


# Backward-compatible alias for tests and e2e overrides.
GuestRateLimiter = MemoryGuestRateLimiter
