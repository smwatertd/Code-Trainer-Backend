"""Curriculum links for TC42 course — 128 tasks × 5 languages, 16 chapters."""

from __future__ import annotations

from migrations.seeds.tc42_course_catalog_generated import CHAPTER_PLANS, build_tc42_course_catalog

TRACK_LANGUAGES = ("python", "cpp", "java", "csharp", "pascal")
TC42_CURRICULUM_TASK_IDS: frozenset[int] = frozenset(range(1, 129))

_IMPL_TYPES = ("block_full", "placeholder", "translation", "debug")

_SNIPPET_PATTERN: dict[str, str] = {
    "python": "tr_python_snippet",
    "cpp": "tr_cpp_snippet",
    "java": "tr_java_snippet",
    "csharp": "tr_csharp_snippet",
}

_DEBUG_PATTERN: dict[str, str] = {
    "python": "dbg_python_logic_fix",
    "cpp": "dbg_cpp_logic_fix",
    "java": "dbg_java_logic_fix",
    "csharp": "dbg_csharp_logic_fix",
    "pascal": "dbg_pascal_logic_fix",
}


def _impl_type(task_id: int) -> str:
    return _IMPL_TYPES[(task_id - 1) % 4]


def _pattern_and_action(language: str, impl: str) -> tuple[str, str]:
    if impl == "block_full":
        if language == "pascal":
            return "asm_blocks_to_code_pascal", "assemble"
        return "tr_pattern_translation", "assemble"
    if impl == "placeholder":
        return "tr_pattern_translation", "assemble"
    if impl == "translation":
        if language == "pascal":
            return "tr_python_to_pascal_code", "translate"
        return _SNIPPET_PATTERN[language], "translate"
    return _DEBUG_PATTERN[language], "debug"


_task_cache: dict[int, dict] | None = None


def _task_by_id() -> dict[int, dict]:
    global _task_cache
    if _task_cache is None:
        _task_cache = {row["id"]: row for row in build_tc42_course_catalog()}
    return _task_cache


def _technical_concept(task_id: int) -> str:
    payload = _task_by_id()[task_id].get("payload") or {}
    constructions = payload.get("constructions") or ["program_entry"]
    return str(constructions[0])


def build_tc42_curriculum_links() -> list[dict]:
    links: list[dict] = []
    for language in TRACK_LANGUAGES:
        for chapter_id, task_ids in CHAPTER_PLANS.items():
            for task_id in task_ids:
                impl = _impl_type(task_id)
                pattern, action = _pattern_and_action(language, impl)
                links.append(
                    {
                        "task_id": task_id,
                        "language": language,
                        "learning_concept_id": chapter_id,
                        "technical_concept_id": _technical_concept(task_id),
                        "exercise_pattern_id": pattern,
                        "action": action,
                        "is_primary": True,
                    },
                )
    return links


CURRICULUM_LINKS_SEED: list[dict] = build_tc42_curriculum_links()
