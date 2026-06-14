from __future__ import annotations

import pytest

from src.core.settings import ExecutionSettings
from src.shared.execution.services.execution_rate_limiter import (
    ExecutionRateLimitError,
    MemoryExecutionRateLimiter,
)


@pytest.fixture
def limiter() -> MemoryExecutionRateLimiter:
    return MemoryExecutionRateLimiter(
        settings=ExecutionSettings(
            global_max_queue=2,
            user_max_per_minute=2,
            user_max_concurrent=1,
            rate_limit_window_seconds=60,
        )
    )


def test_execution_rate_limiter__allows_first_submit(limiter: MemoryExecutionRateLimiter) -> None:
    limiter.check_submit("42", queue_depth=0)
    limiter.on_job_queued("42")
    limiter.on_job_finished("42")


def test_execution_rate_limiter__blocks_global_queue(limiter: MemoryExecutionRateLimiter) -> None:
    with pytest.raises(ExecutionRateLimitError, match="queue is full"):
        limiter.check_submit("42", queue_depth=2)


def test_execution_rate_limiter__blocks_concurrent_jobs(limiter: MemoryExecutionRateLimiter) -> None:
    limiter.check_submit("42", queue_depth=0)
    limiter.on_job_queued("42")

    with pytest.raises(ExecutionRateLimitError, match="concurrent"):
        limiter.check_submit("42", queue_depth=1)


def test_execution_rate_limiter__blocks_per_minute_limit(limiter: MemoryExecutionRateLimiter) -> None:
    limiter.check_submit("42", queue_depth=0)
    limiter.check_submit("42", queue_depth=0)

    with pytest.raises(ExecutionRateLimitError, match="per minute"):
        limiter.check_submit("42", queue_depth=0)
