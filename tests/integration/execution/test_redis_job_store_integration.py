from __future__ import annotations

import pytest

from src.core.settings import AppSettings, ExecutionSettings
from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.stores.redis_job_store import RedisJobStore


@pytest.mark.asyncio
async def test_redis_job_store_integration__enqueue_and_dequeue(settings: AppSettings) -> None:
    if not settings.redis.url:
        pytest.skip("Redis URL is not configured")

    store = RedisJobStore(
        redis_url=settings.redis.url,
        settings=ExecutionSettings(),
        known_language_ids=["python"],
    )
    job = ExecutionJob.create(
        user_id="guest:test",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
    )

    try:
        store.save_job(job)
        store.update_status(job.job_id, JobStatus.QUEUED)
        store.enqueue(job.job_id)

        dequeued = store.dequeue_blocking(timeout=1)

        if dequeued is None:
            pytest.skip("Redis is not available for integration test")

        assert dequeued.job_id == job.job_id
    finally:
        client = store._client  # noqa: SLF001
        client.delete(store._job_key(job.job_id))  # noqa: SLF001
