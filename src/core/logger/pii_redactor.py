from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\-\s()]{8,}\d")

KEY_VALUE_SECRET_RE = re.compile(
    r"(?i)(['\"]?)("
    r"access_token|refresh_token|token|password|code|otp|"
    r"phone|phone_number|email|passport_series_number|birth_date"
    r")(\1\s*[:=]\s*)(['\"]?)([^,'\"\s)\]}]+)(\4)"
)


def redact_pii_text(value: str) -> str:
    redacted = KEY_VALUE_SECRET_RE.sub(r"\1\2\3<redacted>", value)
    redacted = EMAIL_RE.sub("<redacted-email>", redacted)
    redacted = PHONE_RE.sub("<redacted-phone>", redacted)
    return redacted
