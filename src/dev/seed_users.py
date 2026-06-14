from __future__ import annotations

from sqlalchemy import select

from src.core.settings import get_settings
from src.features.auth.models import UserModel
from src.features.auth.services.password_hasher import PasswordHasher
from src.shared.database.database import SqlAlchemyDatabase

DEV_USERS: tuple[dict[str, str], ...] = (
    {
        "name": "Student Dev",
        "email": "student@code-trainer.dev",
        "role": "student",
        "password": "student123",
    },
    {
        "name": "Teacher Dev",
        "email": "teacher@code-trainer.dev",
        "role": "teacher",
        "password": "teacher123",
    },
    {
        "name": "Admin Dev",
        "email": "admin@code-trainer.dev",
        "role": "admin",
        "password": "admin123",
    },
)


async def seed_dev_users() -> None:
    settings = get_settings()
    database = SqlAlchemyDatabase(settings.db)
    hasher = PasswordHasher()

    try:
        async with database.session_factory() as session:
            for spec in DEV_USERS:
                existing = await session.scalar(
                    select(UserModel).where(UserModel.email == spec["email"]),
                )
                if existing is not None:
                    print(f"skip {spec['email']} (already exists)")
                    continue

                session.add(
                    UserModel(
                        name=spec["name"],
                        email=spec["email"],
                        password=hasher.hash(spec["password"]),
                        role=spec["role"],
                    ),
                )
                print(f"created {spec['email']} ({spec['role']})")

            await session.commit()
    finally:
        await database.engine.dispose()
