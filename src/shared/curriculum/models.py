from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LearningConcept:
    id: str
    name_ru: str
    tier: str
    order: int
    description_ru: str = ""


@dataclass(frozen=True)
class TechnicalConcept:
    id: str
    learning_concept_id: str
    name_ru: str
    tier: str


@dataclass(frozen=True)
class ExercisePattern:
    id: str
    action: str
    legacy_adapter: str | None = None


@dataclass(frozen=True)
class TechnicalConceptActionMask:
    technical_concept_id: str
    required_actions: tuple[str, ...]
    optional_actions: tuple[str, ...] = ()
    disabled_actions: tuple[str, ...] = ()
    required_patterns_by_action: dict[str, tuple[str, ...]] = field(default_factory=dict)
    optional_patterns_by_action: dict[str, tuple[str, ...]] = field(default_factory=dict)
    disabled_patterns_by_action: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def active_actions(self) -> tuple[str, ...]:
        disabled = set(self.disabled_actions)
        ordered = [*self.required_actions, *self.optional_actions]
        seen: set[str] = set()
        result: list[str] = []
        for action in ordered:
            if action in disabled or action in seen:
                continue
            seen.add(action)
            result.append(action)
        return tuple(result)

    def patterns_for_action(self, action: str, *, required_only: bool = False) -> tuple[str, ...]:
        disabled = set(self.disabled_patterns_by_action.get(action, ()))
        required = [
            pattern_id for pattern_id in self.required_patterns_by_action.get(action, ()) if pattern_id not in disabled
        ]
        if required_only:
            return tuple(required)
        optional = [
            pattern_id
            for pattern_id in self.optional_patterns_by_action.get(action, ())
            if pattern_id not in disabled and pattern_id not in required
        ]
        return tuple([*required, *optional])


@dataclass(frozen=True)
class CurriculumLinkBundle:
    language: str
    version: int
    learning_concepts: tuple[LearningConcept, ...]
    technical_concepts: tuple[TechnicalConcept, ...]
    exercise_patterns: tuple[ExercisePattern, ...]
    action_masks: dict[str, TechnicalConceptActionMask]

    def learning_concept_by_id(self, learning_concept_id: str) -> LearningConcept | None:
        return next((item for item in self.learning_concepts if item.id == learning_concept_id), None)

    def technical_concept_by_id(self, technical_concept_id: str) -> TechnicalConcept | None:
        return next((item for item in self.technical_concepts if item.id == technical_concept_id), None)

    def pattern_by_id(self, pattern_id: str) -> ExercisePattern | None:
        return next((item for item in self.exercise_patterns if item.id == pattern_id), None)
