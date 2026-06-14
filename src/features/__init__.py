from __future__ import annotations

from fastapi import APIRouter


def get_routers() -> list[APIRouter]:
    from src.features.assignment_sets.router import router as assignment_sets_router
    from src.features.auth.router import router as auth_router
    from src.features.catalog.router import router as catalog_router
    from src.features.catalog.router import teacher_router as teacher_tasks_router
    from src.features.curriculum.router import router as curriculum_router
    from src.features.demo.router import router as demo_router
    from src.features.groups.router import router as groups_router
    from src.features.health.router import router as health_router
    from src.features.languages.router import router as languages_router
    from src.features.progress.curriculum_link_router import router as curriculum_link_router
    from src.features.progress.router import router as progress_router
    from src.features.submissions.router import router as submissions_router

    return [
        health_router,
        languages_router,
        catalog_router,
        teacher_tasks_router,
        demo_router,
        auth_router,
        submissions_router,
        progress_router,
        curriculum_link_router,
        curriculum_router,
        groups_router,
        assignment_sets_router,
    ]
