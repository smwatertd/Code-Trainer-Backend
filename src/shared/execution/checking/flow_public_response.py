from __future__ import annotations

from typing import Any


def sanitize_public_pattern_errors(errors: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Student-facing pattern errors: type + text only, no internal detail fields."""
    sanitized: list[dict[str, str]] = []
    for item in errors:
        if not isinstance(item, dict):
            continue
        error_type = str(item.get("type") or "").strip()
        text = str(item.get("text") or "").strip()
        if not error_type:
            continue
        sanitized.append({"type": error_type, "text": text or error_type})
    return sanitized


def public_flowchart_check_result(result: dict[str, Any]) -> dict[str, Any]:
    """Drop internal validation debug before returning check results to clients."""
    public = dict(result)
    public.pop("flow_debug", None)
    public["pattern_errors"] = sanitize_public_pattern_errors(list(public.get("pattern_errors") or []))
    return public
