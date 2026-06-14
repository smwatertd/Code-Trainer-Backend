from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "w3x4y5z6a7"
down_revision: Union[str, Sequence[str], None] = "v2w3x4y5z6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_WRITE_TASK_IDS = (
    4,
    9,
    10,
    *range(11, 27),
    28,
    29,
    30,
)


def upgrade() -> None:
    schema = get_schema()
    ids_sql = ", ".join(str(task_id) for task_id in _WRITE_TASK_IDS)
    op.execute(sa.text(f"""
            UPDATE "{schema}"."tasks"
            SET task_type = 'task_write_from_description'
            WHERE id IN ({ids_sql})
              AND task_type = 'translation'
            """))


def downgrade() -> None:
    schema = get_schema()
    ids_sql = ", ".join(str(task_id) for task_id in _WRITE_TASK_IDS)
    op.execute(sa.text(f"""
            UPDATE "{schema}"."tasks"
            SET task_type = 'translation'
            WHERE id IN ({ids_sql})
              AND task_type = 'task_write_from_description'
            """))
