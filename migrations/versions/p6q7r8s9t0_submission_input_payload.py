from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from migrations.schema import get_schema

revision: str = "p6q7r8s9t0"
down_revision: Union[str, Sequence[str], None] = "o5p6q7r8s9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    schema = get_schema()
    op.add_column(
        "submission",
        sa.Column("input_payload", sa.JSON(), nullable=True),
        schema=schema,
    )


def downgrade() -> None:
    schema = get_schema()
    op.drop_column("submission", "input_payload", schema=schema)
