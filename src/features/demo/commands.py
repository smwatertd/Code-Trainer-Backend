from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SubmitDemoCheckCommand:
    task_id: int
    language: str
    code: str
    client_ip: str
    block_order: list[int] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    flow: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class GetDemoCheckCommand:
    job_id: str
    client_ip: str
