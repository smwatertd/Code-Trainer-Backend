from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol

import redis

from src.core.settings import ExecutionSettings


class ExecutionRateLimitError(Exception):
    pass


class ExecutionRateLimiterProtocol(Protocol):
    def check_submit(self, user_id: str, *, queue_depth: int) -> None: ...

    def on_job_queued(self, user_id: str) -> None: ...

    def on_job_finished(self, user_id: str) -> None: ...


@dataclass
class MemoryExecutionRateLimiter:
    settings: ExecutionSettings
    _rate_counts: dict[str, tuple[int, datetime]] = field(default_factory=dict)
    _active_counts: dict[str, int] = field(default_factory=dict)

    def check_submit(self, user_id: str, *, queue_depth: int) -> None:
        if queue_depth >= self.settings.global_max_queue:
            raise ExecutionRateLimitError("Execution queue is full. Try again shortly.")

        now = datetime.now(UTC)
        count, expires_at = self._rate_counts.get(user_id, (0, now))
        if now >= expires_at:
            count = 0
            expires_at = now + timedelta(seconds=self.settings.rate_limit_window_seconds)
        count += 1
        self._rate_counts[user_id] = (count, expires_at)
        if count > self.settings.user_max_per_minute:
            raise ExecutionRateLimitError("Too many execution requests per minute.")

        active = self._active_counts.get(user_id, 0)
        if active >= self.settings.user_max_concurrent:
            raise ExecutionRateLimitError("Too many concurrent execution jobs.")

    def on_job_queued(self, user_id: str) -> None:
        self._active_counts[user_id] = self._active_counts.get(user_id, 0) + 1

    def on_job_finished(self, user_id: str) -> None:
        current = self._active_counts.get(user_id, 0)
        if current > 0:
            self._active_counts[user_id] = current - 1


@dataclass
class RedisExecutionRateLimiter:
    settings: ExecutionSettings
    redis_url: str
    _client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def check_submit(self, user_id: str, *, queue_depth: int) -> None:
        if queue_depth >= self.settings.global_max_queue:
            raise ExecutionRateLimitError("Execution queue is full. Try again shortly.")

        rate_key = f"{self.settings.user_rate_prefix}{user_id}"
        count = int(self.client.incr(rate_key))
        if count == 1:
            self.client.expire(rate_key, self.settings.rate_limit_window_seconds)
        if count > self.settings.user_max_per_minute:
            raise ExecutionRateLimitError("Too many execution requests per minute.")

        active_key = self._active_key(user_id)
        active = int(self.client.get(active_key) or 0)
        if active >= self.settings.user_max_concurrent:
            raise ExecutionRateLimitError("Too many concurrent execution jobs.")

    def on_job_queued(self, user_id: str) -> None:
        active_key = self._active_key(user_id)
        count = int(self.client.incr(active_key))
        if count == 1:
            self.client.expire(active_key, self.settings.rate_limit_window_seconds * 2)

    def on_job_finished(self, user_id: str) -> None:
        active_key = self._active_key(user_id)
        current = int(self.client.get(active_key) or 0)
        if current > 0:
            self.client.decr(active_key)

    def _active_key(self, user_id: str) -> str:
        return f"{self.settings.user_lock_prefix}{user_id}:active"


def create_execution_rate_limiter(
    *,
    settings: ExecutionSettings,
    redis_url: str,
    use_redis: bool,
) -> MemoryExecutionRateLimiter | RedisExecutionRateLimiter:
    if use_redis and redis_url:
        return RedisExecutionRateLimiter(settings=settings, redis_url=redis_url)
    return MemoryExecutionRateLimiter(settings=settings)


ExecutionRateLimiter = MemoryExecutionRateLimiter
