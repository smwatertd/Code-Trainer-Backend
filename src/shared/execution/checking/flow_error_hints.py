from __future__ import annotations

from typing import Any


def enrich_flow_pattern_errors(
    errors: list[dict[str, str]],
    debug: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Add student-safe hints. Internal debug (expected sequence, patterns) stays server-side only."""
    if not errors:
        return errors
    if debug is None:
        return errors

    construction_missing = debug.get("construction_missing") or []
    source_failures = debug.get("source_alignment_failures") or []

    enriched: list[dict[str, str]] = []
    for error in errors:
        error_type = str(error.get("type") or "")
        text = str(error.get("text") or "")
        detail_parts: list[str] = []

        if error_type == "FLOW_CONSTRUCTION_MISSING" and construction_missing:
            for item in construction_missing:
                if not isinstance(item, dict):
                    continue
                missing = str(item.get("missing") or "").strip()
                if missing:
                    detail_parts.append(f"Не хватает: {missing}.")

        elif error_type == "FLOW_SOURCE_MISMATCH" and source_failures:
            for item in source_failures:
                if not isinstance(item, dict):
                    continue
                hint = str(item.get("hint") or "").strip()
                if hint:
                    detail_parts.append(hint)

        elif error_type == "FLOW_LOOP_BACK_EDGE":
            detail_parts.append("Проведите стрелку из тела цикла обратно в блок «Цикл» (или «Условие» для while).")

        elif error_type == "FLOW_DECISION_BRANCHES":
            detail_parts.append("Из блока «Условие» должны выходить две стрелки — «да» и «нет».")

        if detail_parts:
            hint = " ".join(detail_parts)
            combined = f"{text}\n{hint}".strip() if text else hint
            enriched.append({**error, "text": combined, "detail": hint})
        else:
            enriched.append(error)

    return enriched
