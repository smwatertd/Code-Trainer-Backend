from __future__ import annotations

from typing import Literal

JobOp = Literal[
    "guest_full_check",
    "full_check",
    "block_reorder_validate",
    "flow_semantic_check",
    "process_submission",
]
