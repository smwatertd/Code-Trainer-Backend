from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DemoCheckRequest(BaseModel):
    task_id: int
    language: str
    code: str = Field(min_length=1, max_length=50_000)
    block_order: list[int] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    flow: list[dict[str, Any]] | None = None


class DemoCheckQueuedResponse(BaseModel):
    job_id: str
    status: str


class DemoCheckResultResponse(BaseModel):
    job_id: str
    status: str
    success: bool | None = None
    compiler_errors: list[dict[str, Any]] = Field(default_factory=list)
    linter_errors: list[dict[str, Any]] = Field(default_factory=list)
    pattern_errors: list[dict[str, Any]] = Field(default_factory=list)
    test_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: str | None = None
