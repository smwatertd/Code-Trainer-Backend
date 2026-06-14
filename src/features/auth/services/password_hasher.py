from __future__ import annotations

import bcrypt


class PasswordHasher:
    def hash(self, raw_password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, raw_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))
