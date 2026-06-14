from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "o5p6q7r8s9"
down_revision: Union[str, Sequence[str], None] = "n4o5p6q7r8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    op.execute(sa.text(f"""
            UPDATE "{schema}"."task_progress" AS tp
            SET passed_count = COALESCE(stats.successes, 0)
            FROM (
                SELECT user_id, task_id, COUNT(*) AS successes
                FROM "{schema}"."submission"
                WHERE success IS TRUE
                  AND user_id IS NOT NULL
                GROUP BY user_id, task_id
            ) AS stats
            WHERE tp.user_id = stats.user_id
              AND tp.task_id = stats.task_id
            """))


def downgrade() -> None:
    pass
