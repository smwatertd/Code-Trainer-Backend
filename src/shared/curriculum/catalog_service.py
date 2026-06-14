from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.either import AppResult, Err, Ok
from src.core.either.failures import NotFoundFailure
from src.shared.curriculum.exceptions import CurriculumNotFoundError
from src.shared.curriculum.loader import load_curriculum_link_bundle, validate_curriculum_link_bundle


@dataclass
class CurriculumCatalogService:
    curriculum_root: Path

    def validate_curriculum(self, language: str) -> AppResult[dict[str, Any]]:
        try:
            bundle = load_curriculum_link_bundle(self.curriculum_root, language, force=True)
        except CurriculumNotFoundError:
            return Err(NotFoundFailure("Curriculum", language))

        errors = validate_curriculum_link_bundle(bundle)
        return Ok(
            {
                "language": bundle.language,
                "valid": not errors,
                "errors": errors,
                "stats": {
                    "learning_concepts": len(bundle.learning_concepts),
                    "technical_concepts": len(bundle.technical_concepts),
                    "exercise_patterns": len(bundle.exercise_patterns),
                    "action_masks": len(bundle.action_masks),
                },
            },
        )

    def get_debug_view(self, language: str) -> AppResult[dict[str, Any]]:
        validation_result = self.validate_curriculum(language)
        if validation_result.is_err():
            return validation_result  # type: ignore[return-value]

        try:
            bundle = load_curriculum_link_bundle(self.curriculum_root, language)
        except CurriculumNotFoundError:
            return Err(NotFoundFailure("Curriculum", language))

        chapters: list[dict[str, Any]] = []
        for learning_concept in sorted(bundle.learning_concepts, key=lambda item: item.order):
            technical_concepts = [
                technical_concept
                for technical_concept in bundle.technical_concepts
                if technical_concept.learning_concept_id == learning_concept.id
            ]
            technical_concepts.sort(key=lambda item: item.id)
            technical_payload: list[dict[str, Any]] = []
            for technical_concept in technical_concepts:
                mask = bundle.action_masks[technical_concept.id]
                technical_payload.append(
                    {
                        "id": technical_concept.id,
                        "name_ru": technical_concept.name_ru,
                        "tier": technical_concept.tier,
                        "required_actions": list(mask.required_actions),
                        "optional_actions": list(mask.optional_actions),
                        "disabled_actions": list(mask.disabled_actions),
                        "active_actions": list(mask.active_actions()),
                        "required_patterns_by_action": {
                            action: list(mask.patterns_for_action(action, required_only=True))
                            for action in mask.active_actions()
                        },
                    },
                )
            chapters.append(
                {
                    "learning_concept": {
                        "id": learning_concept.id,
                        "name_ru": learning_concept.name_ru,
                        "tier": learning_concept.tier,
                        "order": learning_concept.order,
                        "description_ru": learning_concept.description_ru,
                    },
                    "technical_concepts": technical_payload,
                },
            )

        validation = validation_result.value
        return Ok(
            {
                "summary": {
                    "language": bundle.language,
                    "version": bundle.version,
                    "learning_concepts_count": len(bundle.learning_concepts),
                    "technical_concepts_count": len(bundle.technical_concepts),
                    "exercise_patterns_count": len(bundle.exercise_patterns),
                },
                "validation": validation,
                "chapters": chapters,
            },
        )
