from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SubmissionResponse(BaseModel):
    id: int
    user_id: int | None
    task_id: int
    language: str
    status: str
    success: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None
    compiler_errors: list[dict[str, Any]] = Field(default_factory=list)
    linter_errors: list[dict[str, Any]] = Field(default_factory=list)
    pattern_errors: list[dict[str, Any]] = Field(default_factory=list)
    test_results: list[dict[str, Any]] = Field(default_factory=list)
    duration_ms: int | None = None
    code: str = ""
    block_order: list[int] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    flow: list[dict[str, Any]] | None = None


class SubmissionHistoryItemResponse(BaseModel):
    id: int
    task_id: int
    language: str
    status: str
    success: bool | None = None
    created_at: str | None = None
    duration_ms: int | None = None


class SubmissionCreateRequest(BaseModel):
    task_id: int
    language: str
    code: str = Field(min_length=1, max_length=50_000)
    block_order: list[int] | None = None
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    flow: list[dict[str, Any]] | None = None


class SubmissionQueuedResponse(BaseModel):
    id: int
    status: str


class SubmissionAbandonedResponse(BaseModel):
    released: bool
    status: str
