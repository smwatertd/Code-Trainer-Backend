from __future__ import annotations

from alembic import op


def get_schema() -> str:
    context = op.get_context()
    schema = context.config.attributes.get("schema")
    if isinstance(schema, str) and schema:
        return schema
    return "public"
