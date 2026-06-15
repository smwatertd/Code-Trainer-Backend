from __future__ import annotations

from migrations.seeds.basic_program_curriculum_links import (
    CURRICULUM_LINKS_SEED,
    TRACK_BEGINNER_TASK_IDS,
    build_basic_program_curriculum_links,
)


def test_curriculum_links_seed__covers_all_track_languages() -> None:
    assert len(CURRICULUM_LINKS_SEED) == 640

    by_language: dict[str, list[int]] = {}
    for row in CURRICULUM_LINKS_SEED:
        by_language.setdefault(row["language"], []).append(row["task_id"])

    assert sorted(by_language) == ["cpp", "csharp", "java", "pascal", "python"]
    for language in ("python", "cpp", "java", "csharp", "pascal"):
        assert sorted(by_language[language]) == list(range(1, 129))


def test_curriculum_links_seed__python_track_chapters() -> None:
    python_rows = [row for row in CURRICULUM_LINKS_SEED if row["language"] == "python"]
    by_concept: dict[str, list[int]] = {}
    for row in python_rows:
        by_concept.setdefault(row["learning_concept_id"], []).append(row["task_id"])

    assert sorted(by_concept, key=lambda chapter: int(chapter.split("_")[1])) == [
        f"chapter_{index}" for index in range(1, 17)
    ]
    assert by_concept["chapter_1"] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert by_concept["chapter_16"] == list(range(121, 129))


def test_curriculum_links_seed__languages_share_tc42_chapter_plan() -> None:
    by_language: dict[str, set[str]] = {}
    for row in CURRICULUM_LINKS_SEED:
        by_language.setdefault(row["language"], set()).add(row["learning_concept_id"])

    expected = {f"chapter_{index}" for index in range(1, 17)}
    for language in ("python", "cpp", "java", "csharp", "pascal"):
        assert by_language[language] == expected


def test_curriculum_links_seed__task_ids_exist_in_beginner_track() -> None:
    task_ids = {row["task_id"] for row in CURRICULUM_LINKS_SEED}
    assert task_ids == TRACK_BEGINNER_TASK_IDS


def test_build_basic_program_curriculum_links__is_deterministic() -> None:
    assert build_basic_program_curriculum_links() == CURRICULUM_LINKS_SEED
