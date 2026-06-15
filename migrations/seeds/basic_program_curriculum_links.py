"""Backward-compatible re-exports for TC42 curriculum links."""

from __future__ import annotations

from migrations.seeds.tc42_curriculum_links import (
    CURRICULUM_LINKS_SEED,
    TC42_CURRICULUM_TASK_IDS,
    build_tc42_curriculum_links,
)

TRACK_BEGINNER_TASK_IDS = TC42_CURRICULUM_TASK_IDS
BASIC_PROGRAM_CURRICULUM_TASK_IDS = TC42_CURRICULUM_TASK_IDS
BASIC_PROGRAM_CURRICULUM_LINKS = CURRICULUM_LINKS_SEED


def build_basic_program_curriculum_links() -> list[dict]:
    return build_tc42_curriculum_links()
