from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import ConflictFailure, NotFoundFailure, ValidationFailure
from src.core.interfaces import UnitOfWork
from src.features.groups.repos.group_repo import GroupDTO, GroupRepo, InvitationCodeDTO, InvitationCodeRepo


def _to_group_dto(row, member_count: int = 0) -> GroupDTO:
    return GroupDTO(
        id=row.id,
        name=row.name,
        teacher_id=row.teacher_id,
        created_at=row.created_at,
        member_count=member_count,
    )


def _to_invitation_dto(row) -> InvitationCodeDTO:
    return InvitationCodeDTO(
        id=row.id,
        code=row.code,
        group_id=row.group_id,
        max_uses=row.max_uses,
        use_count=row.use_count,
        expires_at=row.expires_at,
        is_active=row.is_active,
    )


def _invitation_valid(row, now: datetime) -> bool:
    if not row.is_active:
        return False
    if row.expires_at is not None and row.expires_at <= now:
        return False
    if row.max_uses is not None and row.use_count >= row.max_uses:
        return False
    return True


@dataclass
class GroupService:
    uow: UnitOfWork

    async def create_group(self, *, teacher_id: int, name: str) -> AppResult[GroupDTO]:
        cleaned = name.strip()
        if not cleaned:
            return Err(ValidationFailure("Group name is required"))
        async with self.uow(autocommit=True) as uow:
            row = await GroupRepo(uow.session).create(name=cleaned, teacher_id=teacher_id)
            return Ok(_to_group_dto(row))

    async def list_teacher_groups(self, teacher_id: int) -> AppResult[list[GroupDTO]]:
        async with self.uow() as uow:
            rows = await GroupRepo(uow.session).list_by_teacher(teacher_id)
            return Ok([_to_group_dto(row, member_count=count) for row, count in rows])

    async def list_student_groups(self, student_id: int) -> AppResult[list[GroupDTO]]:
        async with self.uow() as uow:
            rows = await GroupRepo(uow.session).list_for_student(student_id)
            return Ok([_to_group_dto(row) for row in rows])

    async def create_invitation(
        self,
        *,
        teacher_id: int,
        group_id: int,
        max_uses: int | None,
        expires_in_days: int | None,
    ) -> AppResult[InvitationCodeDTO]:
        async with self.uow(autocommit=True) as uow:
            repo = GroupRepo(uow.session)
            group = await repo.get_by_id(group_id)
            if group is None or group.teacher_id != teacher_id:
                return Err(NotFoundFailure("Group", str(group_id)))

            expires_at = None
            if expires_in_days:
                expires_at = datetime.now(UTC) + timedelta(days=expires_in_days)

            code = secrets.token_urlsafe(8)[:12].upper()
            row = await InvitationCodeRepo(uow.session).create(
                code=code,
                group_id=group_id,
                teacher_id=teacher_id,
                max_uses=max_uses,
                expires_at=expires_at,
            )
            return Ok(_to_invitation_dto(row))

    async def join_by_code(self, *, student_id: int, code: str) -> AppResult[GroupDTO]:
        cleaned = code.strip().upper()
        if not cleaned:
            return Err(ValidationFailure("Invitation code is required"))

        async with self.uow(autocommit=True) as uow:
            groups = GroupRepo(uow.session)
            invitations = InvitationCodeRepo(uow.session)
            invitation = await invitations.get_by_code(cleaned)
            now = datetime.now(UTC)
            if invitation is None or not _invitation_valid(invitation, now):
                return Err(ValidationFailure("Invalid or expired invitation code"))

            group = await groups.get_by_id(invitation.group_id)
            if group is None:
                return Err(NotFoundFailure("Group", str(invitation.group_id)))

            if await groups.is_member(group.id, student_id):
                return Err(ConflictFailure("Already a member of this group"))

            try:
                await groups.add_member(group.id, student_id)
                await invitations.increment_use_count(invitation.id)
            except IntegrityError:
                return Err(ConflictFailure("Already a member of this group"))

            return Ok(_to_group_dto(group))

    async def student_group_ids(self, student_id: int) -> list[int]:
        async with self.uow() as uow:
            return await GroupRepo(uow.session).list_member_group_ids(student_id)

    async def group_owned_by_teacher(self, group_id: int, teacher_id: int) -> bool:
        async with self.uow() as uow:
            group = await GroupRepo(uow.session).get_by_id(group_id)
            return group is not None and group.teacher_id == teacher_id
