from __future__ import annotations

from src.features.auth.services.jti_hasher import JtiHasher


def test_jti_hasher__produces_stable_hex_digest() -> None:
    hasher = JtiHasher(secret_key="test-secret-key-at-least-32-chars-long")

    first = hasher.hash("jti-abc")
    second = hasher.hash("jti-abc")

    assert first == second
    assert len(first) == 64
    assert first != "jti-abc"


def test_jti_hasher__different_jti_produces_different_digest() -> None:
    hasher = JtiHasher(secret_key="test-secret-key-at-least-32-chars-long")

    assert hasher.hash("one") != hasher.hash("two")
