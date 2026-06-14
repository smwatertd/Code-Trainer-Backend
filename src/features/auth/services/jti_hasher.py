from __future__ import annotations

import hashlib
import hmac


class JtiHasher:
    def __init__(self, secret_key: str) -> None:
        self._secret = secret_key.encode("utf-8")

    def hash(self, jti: str) -> str:
        return hmac.new(self._secret, jti.encode("utf-8"), hashlib.sha256).hexdigest()
