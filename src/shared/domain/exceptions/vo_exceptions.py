from __future__ import annotations

from src.shared.domain.exceptions.base import DomainException


class ValueObjectException(DomainException):
    pass


class InvalidEntityId(ValueObjectException):
    def __init__(self, *, entity_id: str, reason: str) -> None:
        super().__init__(f"Invalid entity id: {entity_id}. Reason: {reason}")
