from __future__ import annotations

import json

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.domain.job_status import JobStatus


def test_execution_job__create_has_pending_status() -> None:
    job = ExecutionJob.create(
        user_id="guest:127.0.0.1",
        language_id="python",
        code="print(1)",
        op="guest_full_check",
        task_id=2,
        payload={"guest": True},
    )

    assert job.status == JobStatus.PENDING
    assert job.task_id == 2
    assert job.payload == {"guest": True}
    assert job.job_id


def test_execution_job__json_roundtrip() -> None:
    job = ExecutionJob.create(
        user_id="1",
        language_id="python",
        code="x = 1",
        op="process_submission",
        task_id=1,
        payload={"submission_id": 5},
    )
    job.status = JobStatus.SUCCESS
    job.dedup_key = "dedup-abc"

    restored = ExecutionJob.from_json(job.to_json())

    assert restored.job_id == job.job_id
    assert restored.status == JobStatus.SUCCESS
    assert restored.dedup_key == "dedup-abc"
    assert restored.payload == {"submission_id": 5}


def test_execution_job__to_dict_serializes_status_value() -> None:
    job = ExecutionJob.create(
        user_id="1",
        language_id="python",
        code="pass",
        op="guest_full_check",
    )
    job.status = JobStatus.RUNNING

    data = job.to_dict()
    raw = json.loads(job.to_json())

    assert data["status"] == "RUNNING"
    assert raw["status"] == "RUNNING"
