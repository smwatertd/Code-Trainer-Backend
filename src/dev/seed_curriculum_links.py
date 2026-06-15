from __future__ import annotations

from sqlalchemy import delete, select

from migrations.seeds.tc42_curriculum_links import (
    CURRICULUM_LINKS_SEED,
    TC42_CURRICULUM_TASK_IDS,
)
from src.core.settings import get_settings
from src.features.catalog.models import TaskModel  # noqa: F401
from src.features.progress.models import TaskCurriculumLinkModel
from src.shared.database.database import SqlAlchemyDatabase

_BEGINNER_CHAPTER_IDS = frozenset(
    {f"chapter_{index}" for index in range(1, 17)},
)


def _seed_fingerprint(rows: list[dict]) -> set[tuple[int, str, str, str, str]]:
    return {
        (
            row["task_id"],
            row["language"],
            row["learning_concept_id"],
            row["technical_concept_id"],
            row["exercise_pattern_id"],
        )
        for row in rows
    }


async def seed_dev_curriculum_links() -> None:
    settings = get_settings()
    database = SqlAlchemyDatabase(settings.db)
    task_ids = sorted(TC42_CURRICULUM_TASK_IDS)
    expected = _seed_fingerprint(CURRICULUM_LINKS_SEED)

    try:
        async with database.session_factory() as session:
            await session.execute(
                delete(TaskCurriculumLinkModel).where(
                    TaskCurriculumLinkModel.learning_concept_id.in_(_BEGINNER_CHAPTER_IDS),
                    TaskCurriculumLinkModel.is_primary.is_(True),
                    TaskCurriculumLinkModel.task_id.not_in(task_ids),
                ),
            )

            existing_rows = await session.scalars(
                select(TaskCurriculumLinkModel).where(
                    TaskCurriculumLinkModel.task_id.in_(task_ids),
                    TaskCurriculumLinkModel.is_primary.is_(True),
                ),
            )
            current = _seed_fingerprint(
                [
                    {
                        "task_id": row.task_id,
                        "language": row.language,
                        "learning_concept_id": row.learning_concept_id,
                        "technical_concept_id": row.technical_concept_id,
                        "exercise_pattern_id": row.exercise_pattern_id,
                    }
                    for row in existing_rows
                ],
            )
            if current == expected:
                await session.commit()
                print("skip curriculum links (already seeded)")
                return

            await session.execute(
                delete(TaskCurriculumLinkModel).where(
                    TaskCurriculumLinkModel.task_id.in_(task_ids),
                ),
            )
            session.add_all(TaskCurriculumLinkModel(**row) for row in CURRICULUM_LINKS_SEED)
            await session.commit()
            print(f"seeded {len(CURRICULUM_LINKS_SEED)} curriculum links")
    finally:
        await database.engine.dispose()


async def clear_dev_curriculum_links() -> None:
    """Remove basic-program curriculum links (for tests and reset)."""
    settings = get_settings()
    database = SqlAlchemyDatabase(settings.db)
    task_ids = sorted(TC42_CURRICULUM_TASK_IDS)

    try:
        async with database.session_factory() as session:
            await session.execute(
                delete(TaskCurriculumLinkModel).where(
                    TaskCurriculumLinkModel.task_id.in_(task_ids),
                ),
            )
            await session.commit()
    finally:
        await database.engine.dispose()
