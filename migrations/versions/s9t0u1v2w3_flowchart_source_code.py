from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import build_task_catalog

revision: str = "s9t0u1v2w3"
down_revision: Union[str, Sequence[str], None] = "r8s9t0u1v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    for row in build_task_catalog():
        if row["task_type"] != "task_flowchart_to_code":
            continue
        source_code = row["payload"].get("source_code")
        if not source_code:
            continue

        patch = json.dumps(
            {
                "source_code": source_code,
                "source_language": row["payload"].get("source_language", "python"),
            }
        )
        connection.execute(
            sa.text(f"""
                UPDATE "{schema}"."tasks"
                SET payload = payload::jsonb || CAST(:patch AS jsonb)
                WHERE id = :task_id
                """),
            {"patch": patch, "task_id": row["id"]},
        )


def downgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    connection.execute(sa.text(f"""
            UPDATE "{schema}"."tasks"
            SET payload = payload - 'source_code' - 'source_language'
            WHERE task_type = 'task_flowchart_to_code'
            """))
