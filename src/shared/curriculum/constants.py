from __future__ import annotations

LEARNING_ACTIONS: tuple[str, ...] = (
    "recognize",
    "assemble",
    "translate",
    "analyze",
    "debug",
    "implement",
)

VALID_LEGACY_ADAPTERS: frozenset[str] = frozenset(
    {
        "task_build_from_blocks",
        "task_translate_snippet",
        "task_translate_full_program",
        "task_flowchart_to_code",
    }
)

SUPPORTED_CURRICULUM_LANGUAGES: frozenset[str] = frozenset({"python", "pascal"})
