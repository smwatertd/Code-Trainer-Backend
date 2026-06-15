from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.shared.curriculum.exceptions import CurriculumLinkValidationError, CurriculumNotFoundError
from src.shared.curriculum.loader import load_curriculum_link_bundle


@dataclass(frozen=True)
class CurriculumLinkMetadata:
    language: str
    learning_concept_id: str
    technical_concept_id: str
    exercise_pattern_id: str
    action: str


def validate_task_curriculum_link_metadata(
    curriculum_root: Path,
    *,
    language: str,
    technical_concept_id: str,
    exercise_pattern_id: str,
) -> CurriculumLinkMetadata:
    lang = language.strip().lower()
    try:
        bundle = load_curriculum_link_bundle(curriculum_root, lang)
    except CurriculumNotFoundError as exc:
        raise CurriculumLinkValidationError(str(exc)) from exc

    technical_concept = bundle.technical_concept_by_id(technical_concept_id)
    if technical_concept is None:
        raise CurriculumLinkValidationError(f"Unknown technical concept: {technical_concept_id}")

    pattern = bundle.pattern_by_id(exercise_pattern_id)
    if pattern is None:
        raise CurriculumLinkValidationError(f"Unknown exercise pattern: {exercise_pattern_id}")

    mask = bundle.action_masks.get(technical_concept_id)
    if mask is None:
        raise CurriculumLinkValidationError(f"No action mask for technical concept: {technical_concept_id}")

    action = pattern.action
    if action in mask.disabled_actions:
        raise CurriculumLinkValidationError(
            f"Action {action} is disabled for technical concept {technical_concept_id}",
        )
    if action not in mask.active_actions():
        raise CurriculumLinkValidationError(
            f"Action {action} is not active for technical concept {technical_concept_id}",
        )

    allowed_patterns = set(mask.patterns_for_action(action))
    if allowed_patterns and exercise_pattern_id not in allowed_patterns:
        raise CurriculumLinkValidationError(
            f"Pattern {exercise_pattern_id} is not allowed for {technical_concept_id}/{action}",
        )

    return CurriculumLinkMetadata(
        language=lang,
        learning_concept_id=technical_concept.learning_concept_id,
        technical_concept_id=technical_concept_id,
        exercise_pattern_id=exercise_pattern_id,
        action=action,
    )
