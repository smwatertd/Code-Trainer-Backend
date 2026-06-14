from __future__ import annotations

from src.features.auth.services.password_hasher import PasswordHasher


def test_password_hasher__verify_roundtrip() -> None:
    hasher = PasswordHasher()
    hashed = hasher.hash("password123")

    assert hasher.verify("password123", hashed) is True
    assert hasher.verify("wrong", hashed) is False
