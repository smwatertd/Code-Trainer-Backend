from __future__ import annotations

from src.core.either import Err, Ok
from src.core.either.failures import ForbiddenFailure
from src.core.policies.permissions import Permission
from src.features.auth.services.authorization_service import AuthorizationService


def test_authorization_service__allows_student_solve() -> None:
    service = AuthorizationService()

    result = service.ensure_permission(role="student", permission=Permission.SOLVE_ASSIGNMENTS)

    assert isinstance(result, Ok)


def test_authorization_service__denies_guest_solve() -> None:
    service = AuthorizationService()

    result = service.ensure_permission(role="guest", permission=Permission.SOLVE_ASSIGNMENTS)

    assert isinstance(result, Err)
    assert isinstance(result.error, ForbiddenFailure)


def test_authorization_service__ensure_any_permission() -> None:
    service = AuthorizationService()

    allowed = service.ensure_any_permission(
        role="teacher",
        permissions=(Permission.MANAGE_USERS, Permission.VIEW_STUDENT_RESULTS),
    )
    denied = service.ensure_any_permission(
        role="student",
        permissions=(Permission.MANAGE_USERS, Permission.MANAGE_ROLES),
    )

    assert isinstance(allowed, Ok)
    assert isinstance(denied, Err)
