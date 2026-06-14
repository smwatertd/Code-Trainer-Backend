from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.shared.execution.domain.execution_op import JobOp
from src.shared.execution.domain.job_status import JobStatus


@dataclass
class ExecutionJob:
    job_id: str
    user_id: str
    language_id: str
    code: str
    op: JobOp
    status: JobStatus
    created_at: str
    task_id: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    updated_at: str | None = None
    error: str | None = None
    dedup_key: str | None = None

    @staticmethod
    def now_iso() -> str:
        return datetime.now(UTC).isoformat()

    @classmethod
    def create(
        cls,
        *,
        user_id: str,
        language_id: str,
        code: str,
        op: JobOp,
        task_id: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> ExecutionJob:
        now = cls.now_iso()
        return cls(
            job_id=str(uuid.uuid4()),
            user_id=user_id,
            language_id=language_id,
            code=code,
            op=op,
            status=JobStatus.PENDING,
            created_at=now,
            updated_at=now,
            task_id=task_id,
            payload=dict(payload or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionJob:
        return cls(
            job_id=str(data["job_id"]),
            user_id=str(data["user_id"]),
            language_id=str(data["language_id"]),
            code=str(data["code"]),
            op=data["op"],
            status=JobStatus(str(data["status"])),
            created_at=str(data["created_at"]),
            task_id=int(data["task_id"]) if data.get("task_id") is not None else None,
            payload=dict(data.get("payload") or {}),
            updated_at=data.get("updated_at"),
            error=data.get("error"),
            dedup_key=data.get("dedup_key"),
        )

    @classmethod
    def from_json(cls, raw: str) -> ExecutionJob:
        return cls.from_dict(json.loads(raw))
