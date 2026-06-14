from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import build_task_catalog

revision: str = "u1v2w3x4y5"
down_revision: Union[str, Sequence[str], None] = "t0u1v2w3x4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()

    for row in build_task_catalog():
        if row["id"] not in {40, 44, 48, 49}:
            continue
        patch = json.dumps({"flow_spec": row["payload"]["flow_spec"]})
        connection.execute(
            sa.text(f"""
                UPDATE "{schema}"."tasks"
                SET description = :description,
                    payload = payload::jsonb || CAST(:patch AS jsonb)
                WHERE id = :task_id
                """),
            {
                "description": row["description"],
                "patch": patch,
                "task_id": row["id"],
            },
        )


def downgrade() -> None:
    pass
