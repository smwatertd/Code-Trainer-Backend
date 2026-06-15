from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ForbiddenFailure, NotFoundFailure, ValidationFailure
from src.core.interfaces import UnitOfWork
from src.core.policies.permissions import Permission, can, normalize_role
from src.features.assignment_sets.models import AssignmentSetModel
from src.features.auth.models import UserModel
from src.features.auth.repos.user_repo import UserRepo
from src.features.catalog.models import TaskModel
from src.features.groups.models import StudyGroupModel, group_member_table
from src.features.groups.repos.group_repo import GroupRepo
from src.features.progress.models import StudentCurriculumProgressModel, TaskProgressModel
from src.features.profiles.schemas import (
    MyProfileResponse,
    RecentSubmissionResponse,
    SkillProgressResponse,
    StudentGroupSummaryResponse,
    StudentPublicProfileResponse,
    StudentSummaryResponse,
    StudentTeacherRefResponse,
    TeacherGroupSummaryResponse,
    TeacherPublicProfileResponse,
    TeacherStatsResponse,
)
from src.features.submissions.repos.submission_repo import SubmissionRepo

LEARNING_CONCEPT_LABELS = {
    "conditions": "Условия",
    "loops": "Циклы",
    "functions": "Функции",
    "arrays": "Массивы",
    "strings": "Строки",
    "graphs": "Графы",
}


def _handle(email: str) -> str:
    local = email.split("@", 1)[0]
    return f"@{local}"


def _initials(name: str) -> str:
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:1].upper()
    return (parts[0][:1] + parts[1][:1]).upper()


def _level_label(solved: int) -> str:
    if solved >= 80:
        return "Middle"
    if solved >= 30:
        return "Junior"
    if solved >= 10:
        return "Newcomer"
    return "Beginner"


def _utc_date_key(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    utc_value = value.astimezone(UTC)
    return utc_value.date().isoformat()


def _compute_streak(activity_by_date: dict[str, int]) -> int:
    today = datetime.now(tz=UTC).date()
    streak = 0
    cursor = today
    while True:
        count = activity_by_date.get(cursor.isoformat(), 0)
        if count <= 0:
            break
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _build_activity_by_date(submissions: list) -> dict[str, int]:
    activity: dict[str, int] = defaultdict(int)
    for submission in submissions:
        if submission.created_at is None:
            continue
        activity[_utc_date_key(submission.created_at)] += 1
    return dict(activity)


class ProfileService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_my_profile(self, *, user_id: int) -> AppResult[MyProfileResponse]:
        async with self._uow() as uow:
            session = uow.session
            user = await UserRepo(session).get_by_id(user_id)
            if user is None:
                return Err(NotFoundFailure("User", str(user_id)))

            payload = await self._build_student_payload(session, user, viewer_id=user_id)
            return Ok(
                MyProfileResponse(
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    role=user.role,
                    handle=_handle(user.email),
                    level=payload["level"],
                    solved_tasks_count=payload["solved_count"],
                    total_tasks_attempted=payload["attempted_count"],
                    success_rate=payload["success_rate"],
                    streak_days=payload["streak_days"],
                    groups_count=payload["groups_count"],
                    activity_by_date=payload["activity_by_date"],
                    recent_submissions=payload["recent_submissions"],
                    skills=payload["skills"],
                )
            )

    async def get_user_profile(
        self,
        *,
        target_user_id: int,
        viewer_id: int,
        viewer_role: str,
        teacher_id: int | None = None,
    ) -> AppResult[TeacherPublicProfileResponse | StudentPublicProfileResponse]:
        async with self._uow() as uow:
            session = uow.session
            user_repo = UserRepo(session)
            target = await user_repo.get_by_id(target_user_id)
            if target is None:
                return Err(NotFoundFailure("User", str(target_user_id)))

            role = normalize_role(target.role)
            if role in {"teacher", "admin"}:
                return Ok(await self._build_teacher_profile(session, target, viewer_id))

            if target_user_id == viewer_id:
                payload = await self._build_student_payload(session, target, viewer_id=viewer_id)
                return Ok(self._student_public_from_payload(target, payload, teacher=None, is_own=True))

            if teacher_id is None:
                return Err(ValidationFailure("teacher_id is required for student profiles"))

            if not await self._can_view_student(
                session,
                viewer_id=viewer_id,
                viewer_role=viewer_role,
                teacher_id=teacher_id,
                student_id=target_user_id,
            ):
                return Err(ForbiddenFailure("You cannot view this student profile"))

            teacher = await user_repo.get_by_id(teacher_id)
            if teacher is None:
                return Err(NotFoundFailure("Teacher", str(teacher_id)))

            payload = await self._build_student_payload(session, target, viewer_id=viewer_id)
            return Ok(
                self._student_public_from_payload(
                    target,
                    payload,
                    teacher=StudentTeacherRefResponse(id=teacher.id, name=teacher.name),
                    is_own=False,
                )
            )

    async def _can_view_student(
        self,
        session: AsyncSession,
        *,
        viewer_id: int,
        viewer_role: str,
        teacher_id: int,
        student_id: int,
    ) -> bool:
        if viewer_id == student_id:
            return True
        if normalize_role(viewer_role) == "admin":
            return True
        if viewer_id != teacher_id:
            return False
        if not can(viewer_role, Permission.VIEW_STUDENT_RESULTS):
            return False
        groups = await GroupRepo(session).list_for_student(student_id)
        return any(group.teacher_id == teacher_id for group in groups)

    async def _build_teacher_profile(
        self,
        session: AsyncSession,
        teacher: UserModel,
        viewer_id: int,
    ) -> TeacherPublicProfileResponse:
        group_repo = GroupRepo(session)
        groups_with_counts = await group_repo.list_by_teacher(teacher.id)
        groups = [
            TeacherGroupSummaryResponse(id=group.id, name=group.name, member_count=member_count)
            for group, member_count in groups_with_counts
        ]

        students_count = await session.scalar(
            select(func.count(func.distinct(group_member_table.c.student_id)))
            .select_from(group_member_table)
            .join(StudyGroupModel, group_member_table.c.group_id == StudyGroupModel.id)
            .where(StudyGroupModel.teacher_id == teacher.id)
        )
        if students_count is None:
            students_count = 0

        tasks_count = await session.scalar(
            select(func.count())
            .select_from(TaskModel)
            .where(TaskModel.owner_user_id == teacher.id, TaskModel.is_deleted.is_(False))
        )
        assignment_sets_count = await session.scalar(
            select(func.count())
            .select_from(AssignmentSetModel)
            .where(AssignmentSetModel.teacher_id == teacher.id, AssignmentSetModel.is_archived.is_(False))
        )

        return TeacherPublicProfileResponse(
            user_id=teacher.id,
            name=teacher.name,
            email=teacher.email,
            handle=_handle(teacher.email),
            initials=_initials(teacher.name),
            bio="Преподаватель платформы «Практика кода».",
            groups=groups,
            stats=TeacherStatsResponse(
                tasks_count=int(tasks_count or 0),
                groups_count=len(groups),
                students_count=int(students_count),
                assignment_sets_count=int(assignment_sets_count or 0),
            ),
            is_own_profile=viewer_id == teacher.id,
        )

    async def _build_student_payload(
        self,
        session: AsyncSession,
        user: UserModel,
        *,
        viewer_id: int,
    ) -> dict:
        del viewer_id
        progress_rows = list(
            (await session.scalars(select(TaskProgressModel).where(TaskProgressModel.user_id == user.id))).all()
        )
        solved_count = sum(1 for row in progress_rows if (row.passed_count or 0) > 0)
        attempted_count = sum(row.attempts_count or 0 for row in progress_rows)
        passed_attempts = sum(row.passed_count or 0 for row in progress_rows)
        success_rate = round((passed_attempts / attempted_count) * 100) if attempted_count else 0

        submissions = await SubmissionRepo(session).list_recent_for_user(user_id=user.id, limit=200)
        activity_by_date = _build_activity_by_date(submissions)
        streak_days = _compute_streak(activity_by_date)

        task_ids = {submission.task_id for submission in submissions}
        task_titles: dict[int, str] = {}
        if task_ids:
            rows = await session.execute(
                select(TaskModel.id, TaskModel.title).where(TaskModel.id.in_(task_ids)),
            )
            task_titles = {row.id: row.title for row in rows.all()}

        attempt_by_task: dict[int, int] = defaultdict(int)
        recent_submissions: list[RecentSubmissionResponse] = []
        for submission in submissions[:20]:
            attempt_by_task[submission.task_id] += 1
            status = "accepted" if submission.success else "failed"
            recent_submissions.append(
                RecentSubmissionResponse(
                    id=submission.id,
                    task_id=submission.task_id,
                    task_title=task_titles.get(submission.task_id, f"Задача {submission.task_id}"),
                    language=submission.language,
                    status=status,
                    attempt=attempt_by_task[submission.task_id],
                    created_at=submission.created_at,
                )
            )

        skills = await self._build_skills(session, user.id)
        groups = await GroupRepo(session).list_for_student(user.id)
        teacher_names = await self._teacher_names(session, [group.teacher_id for group in groups])

        last_activity_at = submissions[0].created_at if submissions else None

        return {
            "level": _level_label(solved_count),
            "solved_count": solved_count,
            "attempted_count": attempted_count,
            "success_rate": success_rate,
            "streak_days": streak_days,
            "groups_count": len(groups),
            "activity_by_date": activity_by_date,
            "recent_submissions": recent_submissions,
            "skills": skills,
            "groups": groups,
            "teacher_names": teacher_names,
            "last_activity_at": last_activity_at,
        }

    async def _teacher_names(self, session: AsyncSession, teacher_ids: list[int]) -> dict[int, str]:
        if not teacher_ids:
            return {}
        rows = await session.execute(
            select(UserModel.id, UserModel.name).where(UserModel.id.in_(set(teacher_ids))),
        )
        return {row.id: row.name for row in rows.all()}

    async def _build_skills(self, session: AsyncSession, user_id: int) -> list[SkillProgressResponse]:
        rows = list(
            (
                await session.execute(
                    select(
                        StudentCurriculumProgressModel.learning_concept_id,
                        func.count().label("total"),
                        func.sum(
                            case((StudentCurriculumProgressModel.passed_count > 0, 1), else_=0),
                        ).label("solved"),
                    )
                    .where(StudentCurriculumProgressModel.user_id == user_id)
                    .group_by(StudentCurriculumProgressModel.learning_concept_id)
                )
            ).all()
        )
        if not rows:
            return []

        skills: list[SkillProgressResponse] = []
        for row in rows:
            total = int(row.total or 0)
            solved = int(row.solved or 0)
            if total <= 0:
                continue
            label = LEARNING_CONCEPT_LABELS.get(row.learning_concept_id, row.learning_concept_id)
            skills.append(
                SkillProgressResponse(
                    id=row.learning_concept_id,
                    label=label,
                    percent=round((solved / total) * 100),
                    solved=solved,
                    total=total,
                )
            )
        skills.sort(key=lambda item: item.percent, reverse=True)
        return skills[:5]

    def _student_public_from_payload(
        self,
        user: UserModel,
        payload: dict,
        *,
        teacher: StudentTeacherRefResponse | None,
        is_own: bool,
    ) -> StudentPublicProfileResponse:
        group_repo_groups = payload["groups"]
        teacher_names = payload.get("teacher_names", {})

        groups: list[StudentGroupSummaryResponse] = []
        for group in group_repo_groups:
            groups.append(
                StudentGroupSummaryResponse(
                    id=group.id,
                    name=group.name,
                    teacher_id=group.teacher_id,
                    teacher_name=teacher_names.get(group.teacher_id, f"Преподаватель #{group.teacher_id}"),
                )
            )

        return StudentPublicProfileResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            handle=_handle(user.email),
            initials=_initials(user.name),
            level=payload["level"],
            summary=StudentSummaryResponse(
                solved_count=payload["solved_count"],
                success_rate=payload["success_rate"],
                streak_days=payload["streak_days"],
                attempts_count=payload["attempted_count"],
                last_activity_at=payload["last_activity_at"],
            ),
            groups=groups,
            skills=payload["skills"],
            recent_submissions=payload["recent_submissions"],
            teacher=teacher,
            is_own_profile=is_own,
        )
