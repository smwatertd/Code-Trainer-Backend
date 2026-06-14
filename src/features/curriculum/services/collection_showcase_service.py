from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import NotFoundFailure
from src.core.interfaces import UnitOfWork
from src.features.catalog.models import TaskModel
from src.features.catalog.repos.task_repo import TaskRepo
from src.features.progress.models import TaskCurriculumLinkModel
from src.features.progress.repos.curriculum_progress_repo import CurriculumProgressRepo
from src.features.progress.repos.task_curriculum_link_repo import TaskCurriculumLinkRepo
from src.features.progress.services.task_progress_service import progress_status_from_row
from src.shared.curriculum.exceptions import CurriculumNotFoundError
from src.shared.curriculum.loader import load_curriculum_link_bundle


def _progress_percent(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * passed / total, 1)


ACTION_LABELS: dict[str, str] = {
    "translate": "Перенести",
    "assemble": "Собрать",
    "implement": "Реализовать",
    "debug": "Отладить",
    "analyze": "Разобрать",
    "recognize": "Опознать",
}

TASK_TYPE_ACTION: dict[str, str] = {
    "translation": "translate",
    "task_build_from_blocks": "assemble",
    "task_write_from_description": "implement",
    "task_flowchart_to_code": "implement",
    "algorithm": "implement",
}

DIFFICULTY_LABELS: dict[str, str] = {
    "easy": "Лёгкая",
    "medium": "Средняя",
    "hard": "Сложная",
}


LANGUAGE_LABELS: dict[str, str] = {
    "python": "Python",
    "pascal": "Pascal",
    "java": "Java",
    "cpp": "C++",
    "csharp": "C#",
}


@dataclass
class CollectionShowcaseService:
    curriculum_root: Path
    uow: UnitOfWork

    async def build_collections_view(
        self,
        language: str,
        user_id: int | None,
    ) -> AppResult[dict]:
        lang = language.strip().lower()
        try:
            bundle = load_curriculum_link_bundle(self.curriculum_root, lang)
        except CurriculumNotFoundError:
            return Err(NotFoundFailure("Curriculum", lang))

        async with self.uow():
            session = self.uow.session
            link_repo = TaskCurriculumLinkRepo(session)
            collections: list[dict] = []
            aggregate_passed = 0
            aggregate_total = 0

            for learning_concept in sorted(bundle.learning_concepts, key=lambda item: item.order):
                summary = await self._build_collection_summary(
                    session=session,
                    bundle_language=lang,
                    learning_concept_id=learning_concept.id,
                    title_ru=learning_concept.name_ru,
                    description_ru=learning_concept.description_ru,
                    order=learning_concept.order,
                    user_id=user_id,
                    link_repo=link_repo,
                )
                collections.append(summary)
                aggregate_passed += summary["progress"]["passed_tasks"]
                aggregate_total += summary["progress"]["total_tasks"]

            return Ok(
                {
                    "language": lang,
                    "language_label": LANGUAGE_LABELS.get(lang, lang.capitalize()),
                    "progress": {
                        "total_tasks": aggregate_total,
                        "passed_tasks": aggregate_passed,
                        "progress_percent": _progress_percent(aggregate_passed, aggregate_total),
                    },
                    "collections": collections,
                },
            )

    async def build_collection_showcase(
        self,
        language: str,
        learning_concept_id: str,
        user_id: int | None,
    ) -> AppResult[dict]:
        lang = language.strip().lower()
        concept_id = learning_concept_id.strip()
        try:
            bundle = load_curriculum_link_bundle(self.curriculum_root, lang)
        except CurriculumNotFoundError:
            return Err(NotFoundFailure("Curriculum", lang))

        learning_concept = bundle.learning_concept_by_id(concept_id)
        if learning_concept is None:
            return Err(NotFoundFailure("LearningConcept", concept_id))

        async with self.uow():
            session = self.uow.session
            link_repo = TaskCurriculumLinkRepo(session)
            links = await link_repo.list_for_learning_concept(
                language=lang,
                learning_concept_id=concept_id,
            )
            task_ids = [link.task_id for link in links]
            tasks_by_id = await self._load_tasks_by_id(session, task_ids)
            progress_by_task = await self._load_progress_by_task(session, user_id, task_ids)

            sections: list[dict] = []
            for technical_concept in bundle.technical_concepts:
                if technical_concept.learning_concept_id != concept_id:
                    continue
                section_links = [link for link in links if link.technical_concept_id == technical_concept.id]
                if not section_links:
                    continue
                section_tasks = [
                    self._build_showcase_task(
                        task=tasks_by_id[link.task_id],
                        link=link,
                        progress=progress_by_task.get(link.task_id),
                        subtopic_name_ru=technical_concept.name_ru,
                    )
                    for link in sorted(section_links, key=lambda item: item.task_id)
                    if link.task_id in tasks_by_id
                ]
                if not section_tasks:
                    continue
                tc_passed = sum(1 for task in section_tasks if task["progress_status"] == "passed")
                sections.append(
                    {
                        "id": technical_concept.id,
                        "name_ru": technical_concept.name_ru,
                        "tasks": section_tasks,
                        "progress": {
                            "total_tasks": len(section_tasks),
                            "passed_tasks": tc_passed,
                            "progress_percent": _progress_percent(tc_passed, len(section_tasks)),
                        },
                    },
                )

            total_tasks = sum(section["progress"]["total_tasks"] for section in sections)
            passed_tasks = sum(section["progress"]["passed_tasks"] for section in sections)
            next_task = self._find_next_task(sections)

            return Ok(
                {
                    "collection_id": concept_id,
                    "title": learning_concept.name_ru,
                    "description": learning_concept.description_ru,
                    "total_tasks": total_tasks,
                    "progress": {
                        "total_tasks": total_tasks,
                        "passed_tasks": passed_tasks,
                        "progress_percent": _progress_percent(passed_tasks, total_tasks),
                    }
                    if user_id is not None
                    else None,
                    "sections": sections,
                    "next_task": next_task,
                    "button_label": self._button_label(passed_tasks, total_tasks, next_task is not None),
                    "completed": total_tasks > 0 and passed_tasks >= total_tasks,
                },
            )

    async def _build_collection_summary(
        self,
        *,
        session: AsyncSession,
        bundle_language: str,
        learning_concept_id: str,
        title_ru: str,
        description_ru: str,
        order: int,
        user_id: int | None,
        link_repo: TaskCurriculumLinkRepo,
    ) -> dict:
        links = await link_repo.list_for_learning_concept(
            language=bundle_language,
            learning_concept_id=learning_concept_id,
        )
        task_ids = [link.task_id for link in links]
        tasks_by_id = await self._load_tasks_by_id(session, task_ids)
        progress_by_task = await self._load_progress_by_task(session, user_id, task_ids)

        passed = 0
        next_task: dict | None = None
        for link in sorted(links, key=lambda item: item.task_id):
            if link.task_id not in tasks_by_id:
                continue
            status = progress_by_task.get(link.task_id)
            if status == "passed":
                passed += 1
            elif next_task is None:
                task = tasks_by_id[link.task_id]
                next_task = {
                    "task_id": link.task_id,
                    "title": task.title,
                    "progress_status": status or "not_started",
                }

        total = len([link for link in links if link.task_id in tasks_by_id])
        completed = total > 0 and passed >= total

        return {
            "collection_id": learning_concept_id,
            "title_ru": title_ru,
            "description_ru": description_ru,
            "route_path": f"/learn/{bundle_language}/{learning_concept_id}",
            "order": order,
            "progress": {
                "total_tasks": total,
                "passed_tasks": passed,
                "progress_percent": _progress_percent(passed, total),
            },
            "completed": completed,
            "button_label": self._button_label(passed, total, next_task is not None),
            "next_task": next_task,
        }

    async def _load_tasks_by_id(
        self,
        session: AsyncSession,
        task_ids: list[int],
    ) -> dict[int, TaskModel]:
        if not task_ids:
            return {}
        repo = TaskRepo(session)
        result: dict[int, TaskModel] = {}
        for task_id in task_ids:
            task = await repo.get_public(task_id)
            if task is not None:
                result[task_id] = task
        return result

    async def _load_progress_by_task(
        self,
        session: AsyncSession,
        user_id: int | None,
        task_ids: list[int],
    ) -> dict[int, str]:
        if user_id is None or not task_ids:
            return {}
        rows = await CurriculumProgressRepo(session).list_for_user_tasks(user_id, task_ids)
        return {row.task_id: progress_status_from_row(row) for row in rows}

    def _build_showcase_task(
        self,
        *,
        task: TaskModel,
        link: TaskCurriculumLinkModel,
        progress: str | None,
        subtopic_name_ru: str,
    ) -> dict:
        action = link.action or TASK_TYPE_ACTION.get(task.task_type, "implement")
        action_label = ACTION_LABELS.get(action, action)
        language_label = link.language.capitalize()
        return {
            "task_id": task.id,
            "title": task.title,
            "action": action,
            "action_label": action_label,
            "action_skill_label": f"{action_label} · {language_label}",
            "action_description_ru": task.description,
            "difficulty": DIFFICULTY_LABELS.get(task.difficulty, task.difficulty),
            "progress_status": progress,
            "short_instruction": task.description,
            "subtopic_name_ru": subtopic_name_ru,
        }

    def _find_next_task(self, sections: list[dict]) -> dict | None:
        for section in sections:
            for task in section["tasks"]:
                if task.get("progress_status") != "passed":
                    return {
                        "task_id": task["task_id"],
                        "title": task["title"],
                        "progress_status": task.get("progress_status") or "not_started",
                    }
        return None

    def _button_label(self, passed: int, total: int, has_next: bool) -> str:
        if total <= 0:
            return "Нет задач"
        if passed >= total:
            return "Повторить"
        if passed > 0 or has_next:
            return "Продолжить"
        return "Начать"
