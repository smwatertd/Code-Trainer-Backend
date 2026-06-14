from __future__ import annotations

import json
from typing import Any

import redis

from src.core.settings import ExecutionSettings
from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus
from src.shared.execution.interfaces.job_store import JobStore


class JobStoreError(Exception):
    pass


class RedisJobStore(JobStore):
    def __init__(
        self,
        *,
        redis_url: str,
        settings: ExecutionSettings,
        known_language_ids: list[str] | None = None,
        client: redis.Redis | None = None,
    ) -> None:
        self._settings = settings
        self._known_language_ids = {lang.lower() for lang in (known_language_ids or [])}
        self._client = client or redis.from_url(redis_url, decode_responses=True)

    def queue_name_for_language(self, language_id: str) -> str:
        lang = str(language_id).lower()
        if lang in self._known_language_ids:
            return f"{self._settings.queue_prefix}:{lang}"
        return self._settings.queue_default

    def list_queue_names(self) -> list[str]:
        names = [self.queue_name_for_language(lang_id) for lang_id in sorted(self._known_language_ids)]
        if self._settings.queue_default not in names:
            names.append(self._settings.queue_default)
        return names

    def _job_key(self, job_id: str) -> str:
        return f"{self._settings.job_key_prefix}{job_id}"

    def _result_key(self, job_id: str) -> str:
        return f"{self._settings.result_key_prefix}{job_id}"

    def _dedup_key(self, dedup_key: str) -> str:
        return f"{self._settings.dedup_key_prefix}{dedup_key}"

    def get_dedup_job_id(self, dedup_key: str) -> str | None:
        return self._client.get(self._dedup_key(dedup_key))

    def bind_dedup(self, dedup_key: str, job_id: str) -> None:
        self._client.set(
            self._dedup_key(dedup_key),
            job_id,
            ex=self._settings.job_ttl_seconds,
        )

    def save_job(self, job: ExecutionJob) -> None:
        self._client.set(
            self._job_key(job.job_id),
            job.to_json(),
            ex=self._settings.job_ttl_seconds,
        )

    def get_job(self, job_id: str) -> ExecutionJob | None:
        raw = self._client.get(self._job_key(job_id))
        if not raw:
            return None
        return ExecutionJob.from_json(raw)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error: str | None = None,
    ) -> ExecutionJob | None:
        job = self.get_job(job_id)
        if not job:
            return None
        job.status = status
        job.updated_at = ExecutionJob.now_iso()
        if error is not None:
            job.error = error
        self.save_job(job)
        return job

    def save_result(self, job_id: str, result: dict[str, Any]) -> None:
        body = {"job_id": job_id, **result}
        self._client.set(
            self._result_key(job_id),
            json.dumps(body),
            ex=self._settings.job_ttl_seconds,
        )

    def get_result(self, job_id: str) -> dict[str, Any] | None:
        raw = self._client.get(self._result_key(job_id))
        if not raw:
            return None
        return json.loads(raw)

    def enqueue(self, job_id: str) -> None:
        job = self.get_job(job_id)
        if not job:
            raise JobStoreError(f"Job {job_id} not found")
        queue = self.queue_name_for_language(job.language_id)
        self._client.lpush(queue, job_id)
        self._client.incr(self._settings.global_depth_key)

    def dequeue(self) -> str | None:
        job = self.dequeue_blocking(timeout=0)
        return job.job_id if job else None

    def dequeue_blocking(self, timeout: int) -> ExecutionJob | None:
        item = self._client.brpop(self.list_queue_names(), timeout=timeout)
        if not item:
            return None
        _, job_id = item
        return self.get_job(job_id)

    def decrement_queue_depth(self) -> None:
        depth = int(self._client.get(self._settings.global_depth_key) or 0)
        if depth > 0:
            self._client.decr(self._settings.global_depth_key)

    def queue_depth(self) -> int:
        return int(self._client.get(self._settings.global_depth_key) or 0)
