from __future__ import annotations

from typing import Sequence, Union

revision: str = "f3a4b5c6d7_prog_links"
down_revision: Union[str, Sequence[str], None] = "e2f3a4b5c6_placeholder_capstones"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Revision anchor only — curriculum links are seeded via `python -m src.cli seed-dev`."""
    return None


def downgrade() -> None:
    return None
