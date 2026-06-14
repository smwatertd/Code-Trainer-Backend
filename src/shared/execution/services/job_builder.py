from __future__ import annotations

import hashlib
import json
from typing import Any

from src.shared.execution.domain.execution_op import JobOp


def build_dedup_key(
    *,
    user_id: str,
    task_id: int | None,
    code: str,
    op: JobOp,
    language_id: str,
    payload: dict[str, Any] | None = None,
) -> str:
    if op == "process_submission" and payload and payload.get("submission_id") is not None:
        return f"submission:{payload['submission_id']}:{op}"

    raw = f"{user_id}:{task_id}:{language_id}:{op}:{code}"
    if payload:
        raw += (
            ":"
            + hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode("utf-8"),
            ).hexdigest()[:16]
        )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
