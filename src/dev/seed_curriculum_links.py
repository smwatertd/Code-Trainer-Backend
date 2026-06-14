from __future__ import annotations

from sqlalchemy import delete, select

from migrations.seeds.basic_program_curriculum_links import CURRICULUM_LINKS_SEED
from src.core.settings import get_settings
from src.features.catalog.models import TaskModel  # noqa: F401
from src.features.progress.models import TaskCurriculumLinkModel
from src.shared.database.database import SqlAlchemyDatabase


async def seed_dev_curriculum_links() -> None:
    settings = get_settings()
    database = SqlAlchemyDatabase(settings.db)
    task_ids = sorted({row["task_id"] for row in CURRICULUM_LINKS_SEED})

    try:
        async with database.session_factory() as session:
            existing_task_ids = set(
                await session.scalars(
                    select(TaskCurriculumLinkModel.task_id)
                    .where(TaskCurriculumLinkModel.task_id.in_(task_ids))
                    .distinct(),
                ),
            )
            if existing_task_ids == set(task_ids):
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
