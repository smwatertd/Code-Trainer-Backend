from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.shared.curriculum.constants import (
    LEARNING_ACTIONS,
    SUPPORTED_CURRICULUM_LANGUAGES,
    VALID_LEGACY_ADAPTERS,
)
from src.shared.curriculum.exceptions import CurriculumNotFoundError
from src.shared.curriculum.models import (
    CurriculumLinkBundle,
    ExercisePattern,
    LearningConcept,
    TechnicalConcept,
    TechnicalConceptActionMask,
)

_CACHE: dict[str, CurriculumLinkBundle] = {}


def _curriculum_dir(root: Path, language: str) -> Path:
    lang = language.strip().lower()
    if lang not in SUPPORTED_CURRICULUM_LANGUAGES:
        raise CurriculumNotFoundError(f"Unsupported curriculum language: {language}")
    return root / lang


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CurriculumNotFoundError(f"Missing curriculum file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CurriculumNotFoundError(f"{path.name}: root must be a mapping")
    return data


def _parse_learning_concepts(raw: dict[str, Any]) -> tuple[LearningConcept, ...]:
    items = raw.get("concepts") or []
    return tuple(
        LearningConcept(
            id=str(item["id"]),
            name_ru=str(item.get("name_ru", "")),
            tier=str(item.get("tier", "")),
            order=int(item.get("order", 0)),
            description_ru=str(item.get("description_ru", "")),
        )
        for item in items
    )


def _parse_technical_concepts(raw: dict[str, Any]) -> tuple[TechnicalConcept, ...]:
    items = raw.get("concepts") or []
    return tuple(
        TechnicalConcept(
            id=str(item["id"]),
            learning_concept_id=str(item["learning_concept_id"]),
            name_ru=str(item.get("name_ru", "")),
            tier=str(item.get("tier", "beginner")),
        )
        for item in items
    )


def _parse_exercise_patterns(raw: dict[str, Any]) -> tuple[ExercisePattern, ...]:
    items = raw.get("patterns") or []
    result: list[ExercisePattern] = []
    for item in items:
        legacy = item.get("legacy_adapter")
        result.append(
            ExercisePattern(
                id=str(item["id"]),
                action=str(item["action"]),
                legacy_adapter=str(legacy) if legacy else None,
            ),
        )
    return tuple(result)


def _patterns_map(raw: dict[str, Any], key: str) -> dict[str, tuple[str, ...]]:
    block = raw.get(key) or {}
    if not isinstance(block, dict):
        return {}
    result: dict[str, tuple[str, ...]] = {}
    for action, pattern_ids in block.items():
        if isinstance(pattern_ids, list):
            result[str(action)] = tuple(str(pattern_id) for pattern_id in pattern_ids)
    return result


def _parse_action_mask_entry(technical_concept_id: str, raw: dict[str, Any]) -> TechnicalConceptActionMask:
    return TechnicalConceptActionMask(
        technical_concept_id=technical_concept_id,
        required_actions=tuple(str(action) for action in (raw.get("required_actions") or [])),
        optional_actions=tuple(str(action) for action in (raw.get("optional_actions") or [])),
        disabled_actions=tuple(str(action) for action in (raw.get("disabled_actions") or [])),
        required_patterns_by_action=_patterns_map(raw, "required_patterns_by_action"),
        optional_patterns_by_action=_patterns_map(raw, "optional_patterns_by_action"),
        disabled_patterns_by_action=_patterns_map(raw, "disabled_patterns_by_action"),
    )


def _build_default_mask(
    technical_concept: TechnicalConcept,
    tier_defaults: dict[str, dict[str, list[str]]],
) -> TechnicalConceptActionMask:
    tier_cfg = tier_defaults.get(technical_concept.tier, {})
    return TechnicalConceptActionMask(
        technical_concept_id=technical_concept.id,
        required_actions=tuple(tier_cfg.get("required_actions") or []),
        optional_actions=tuple(tier_cfg.get("optional_actions") or []),
        disabled_actions=tuple(tier_cfg.get("disabled_actions") or []),
    )


def load_curriculum_link_bundle(
    root: Path,
    language: str,
    *,
    force: bool = False,
) -> CurriculumLinkBundle:
    lang = language.strip().lower()
    if not force and lang in _CACHE:
        return _CACHE[lang]

    base = _curriculum_dir(root, lang)
    learning_raw = _read_yaml(base / "learning_concepts.yaml")
    learning_concepts = _parse_learning_concepts(learning_raw)
    technical_concepts = _parse_technical_concepts(_read_yaml(base / "technical_concepts.yaml"))
    exercise_patterns = _parse_exercise_patterns(_read_yaml(base / "exercise_pattern_catalog.yaml"))
    matrix_raw = _read_yaml(base / "tc_action_matrix.yaml")
    tier_defaults = dict(matrix_raw.get("tier_defaults") or {})
    explicit_masks_raw = matrix_raw.get("action_masks") or {}

    action_masks: dict[str, TechnicalConceptActionMask] = {}
    for technical_concept in technical_concepts:
        explicit = explicit_masks_raw.get(technical_concept.id)
        if isinstance(explicit, dict):
            action_masks[technical_concept.id] = _parse_action_mask_entry(technical_concept.id, explicit)
        else:
            action_masks[technical_concept.id] = _build_default_mask(technical_concept, tier_defaults)

    for pattern in exercise_patterns:
        if pattern.action not in LEARNING_ACTIONS:
            raise CurriculumNotFoundError(
                f"Pattern {pattern.id} in {lang} curriculum has unknown action {pattern.action}",
            )

    bundle = CurriculumLinkBundle(
        language=lang,
        version=int(learning_raw.get("version", 1)),
        learning_concepts=learning_concepts,
        technical_concepts=technical_concepts,
        exercise_patterns=exercise_patterns,
        action_masks=action_masks,
    )
    _CACHE[lang] = bundle
    return bundle


def validate_curriculum_link_bundle(bundle: CurriculumLinkBundle) -> list[str]:
    errors: list[str] = []
    pattern_ids = {pattern.id for pattern in bundle.exercise_patterns}
    pattern_by_id = {pattern.id: pattern for pattern in bundle.exercise_patterns}
    learning_concept_ids = {item.id for item in bundle.learning_concepts}
    technical_concept_ids = {item.id for item in bundle.technical_concepts}

    if len(bundle.learning_concepts) != len(learning_concept_ids):
        errors.append("Duplicate learning concept ids")

    if len(bundle.technical_concepts) != len(technical_concept_ids):
        errors.append("Duplicate technical concept ids")

    for technical_concept in bundle.technical_concepts:
        if technical_concept.learning_concept_id not in learning_concept_ids:
            errors.append(
                f"TC {technical_concept.id}: unknown learning_concept_id {technical_concept.learning_concept_id}",
            )

    for pattern in bundle.exercise_patterns:
        if pattern.action not in LEARNING_ACTIONS:
            errors.append(f"Pattern {pattern.id}: unknown action {pattern.action}")
        if pattern.legacy_adapter and pattern.legacy_adapter not in VALID_LEGACY_ADAPTERS:
            errors.append(f"Pattern {pattern.id}: invalid legacy_adapter {pattern.legacy_adapter}")

    for technical_concept_id, mask in bundle.action_masks.items():
        if technical_concept_id not in technical_concept_ids:
            errors.append(f"Action mask unknown TC: {technical_concept_id}")
            continue
        if not mask.required_actions:
            errors.append(f"TC {technical_concept_id}: required_actions must not be empty")

        disabled = set(mask.disabled_actions)
        for action in mask.required_actions:
            if action not in LEARNING_ACTIONS:
                errors.append(f"TC {technical_concept_id}: unknown required action {action}")
            if action in disabled:
                errors.append(f"TC {technical_concept_id}: required action {action} is disabled")

        for action in mask.optional_actions:
            if action in disabled:
                errors.append(f"TC {technical_concept_id}: optional action {action} is disabled")

        all_actions = set(mask.required_actions) | set(mask.optional_actions) | disabled
        for action in all_actions:
            for bucket in (
                mask.required_patterns_by_action.get(action, ()),
                mask.optional_patterns_by_action.get(action, ()),
                mask.disabled_patterns_by_action.get(action, ()),
            ):
                for pattern_id in bucket:
                    if pattern_id not in pattern_ids:
                        errors.append(f"TC {technical_concept_id}/{action}: unknown pattern {pattern_id}")
                    else:
                        pattern = pattern_by_id[pattern_id]
                        if pattern.action != action:
                            errors.append(
                                f"TC {technical_concept_id}/{action}: pattern {pattern_id} has action {pattern.action}",
                            )

            for pattern_id in mask.required_patterns_by_action.get(action, ()):
                if pattern_id in set(mask.disabled_patterns_by_action.get(action, ())):
                    errors.append(
                        f"TC {technical_concept_id}/{action}: required pattern {pattern_id} is disabled",
                    )

        for action in disabled:
            if mask.required_patterns_by_action.get(action):
                errors.append(f"TC {technical_concept_id}: disabled action {action} has required patterns")

    return errors


def clear_curriculum_cache() -> None:
    _CACHE.clear()
