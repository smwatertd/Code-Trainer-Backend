from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema
from migrations.seeds.task_catalog_seed import FLOWCHART_TEST_CASES, build_task_catalog

revision: str = "v2w3x4y5z6"
down_revision: Union[str, Sequence[str], None] = "u1v2w3x4y5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FLOWCHART_IDS = [3, 6, *range(39, 51)]


def upgrade() -> None:
    schema = get_schema()
    connection = op.get_bind()
    catalog = {row["id"]: row for row in build_task_catalog()}

    for task_id in FLOWCHART_IDS:
        row = catalog[task_id]
        test_cases = row["payload"].get("test_cases") or FLOWCHART_TEST_CASES.get(task_id)
        if not test_cases:
            continue
        patch = json.dumps({"test_cases": test_cases, "flow_spec": row["payload"]["flow_spec"]})
        connection.execute(
            sa.text(f"""
                UPDATE "{schema}"."tasks"
                SET payload = payload::jsonb || CAST(:patch AS jsonb)
                WHERE id = :task_id
                """),
            {"patch": patch, "task_id": task_id},
        )


def downgrade() -> None:
    pass
