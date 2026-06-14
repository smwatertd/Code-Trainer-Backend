from __future__ import annotations

from src.core.settings import ExecutionSettings
from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.stores.redis_job_store import RedisJobStore


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._lists: dict[str, list[str]] = {}
        self._counters: dict[str, int] = {}

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        _ = ex
        self._data[key] = value
        return True

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def lpush(self, key: str, value: str) -> int:
        self._lists.setdefault(key, []).insert(0, value)
        return len(self._lists[key])

    def brpop(self, keys: list[str], timeout: int) -> tuple[str, str] | None:
        _ = timeout
        for key in keys:
            values = self._lists.get(key) or []
            if values:
                job_id = values.pop()
                return key, job_id
        return None

    def incr(self, key: str) -> int:
        self._counters[key] = int(self._counters.get(key, 0)) + 1
        return self._counters[key]

    def decr(self, key: str) -> int:
        self._counters[key] = max(0, int(self._counters.get(key, 0)) - 1)
        return self._counters[key]


def _store(*, known_language_ids: list[str] | None = None) -> RedisJobStore:
    return RedisJobStore(
        redis_url="redis://localhost:6379/0",
        settings=ExecutionSettings(),
        known_language_ids=known_language_ids or ["python"],
        client=_FakeRedis(),  # type: ignore[arg-type]
    )


def test_redis_job_store__enqueue_uses_language_partition() -> None:
    store = _store()
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
    )
    store.save_job(job)
    store.enqueue(job.job_id)

    queue = store.queue_name_for_language("python")
    assert store._client._lists[queue] == [job.job_id]  # noqa: SLF001


def test_redis_job_store__roundtrip_job_and_result() -> None:
    store = _store()
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="cpp",
        code="cout << 1;",
        op="guest_full_check",
    )
    store.save_job(job)
    loaded = store.get_job(job.job_id)

    assert loaded is not None
    assert loaded.code == "cout << 1;"

    store.save_result(job.job_id, {"status": "SUCCESS", "output": {"success": True}})
    result = store.get_result(job.job_id)

    assert result is not None
    assert result["output"] == {"success": True}


def test_redis_job_store__dequeue_blocking_returns_job() -> None:
    store = _store(known_language_ids=["python"])
    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
    )
    store.save_job(job)
    store.update_status(job.job_id, JobStatus.QUEUED)
    store.enqueue(job.job_id)

    dequeued = store.dequeue_blocking(timeout=0)

    assert dequeued is not None
    assert dequeued.job_id == job.job_id


def test_redis_job_store__unknown_language_uses_default_queue() -> None:
    store = _store(known_language_ids=["python"])
    assert store.queue_name_for_language("haskell") == ExecutionSettings().queue_default
