from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GroupResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    created_at: datetime | None = None
    member_count: int = 0


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class JoinGroupRequest(BaseModel):
    code: str = Field(min_length=4, max_length=32)


class GenerateInvitationRequest(BaseModel):
    max_uses: int | None = Field(default=None, ge=1)
    expires_in_days: int | None = Field(default=30, ge=1, le=365)


class InvitationCodeResponse(BaseModel):
    id: int
    code: str
    group_id: int
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    is_active: bool


class GroupMemberResponse(BaseModel):
    id: int
    name: str
    email: str


class GroupAssignmentSetSummaryResponse(BaseModel):
    id: int
    name: str
    task_count: int
    deadline_at: datetime | None = None


class GroupStudentSummaryResponse(BaseModel):
    student_id: int
    student_name: str
    solved_count: int
    total_tasks: int
    progress_percent: float


class StudentTaskProgressResponse(BaseModel):
    student_id: int
    task_id: int
    progress_status: str
    attempts_count: int


class GroupDashboardResponse(BaseModel):
    group: GroupResponse
    members: list[GroupMemberResponse]
    assignment_sets: list[GroupAssignmentSetSummaryResponse]
    student_summaries: list[GroupStudentSummaryResponse]
    task_progress: list[StudentTaskProgressResponse]
