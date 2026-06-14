"""PASS/FAIL — concepts.yml ast_nodes + grade(required ⊆ detected)."""

from __future__ import annotations

from src.shared.analysis.concept_ast_detector import (
    concept_label,
    detect_concepts,
)
from src.shared.analysis.domain.semantic_core import (
    CoreDetectionResult,
    ExamResult,
    RequiredStructureSpec,
)
from src.shared.analysis.educational_vocabulary import (
    get_exam_structure_ids,
    map_required_type,
    normalize_construction_tags,
)
from src.shared.analysis.grade import grade
from src.shared.analysis.tree_sitter_gateway import parse_code


class EducationalValidator:
    def validate(
        self,
        code: str,
        language_id: str,
        required: list[RequiredStructureSpec] | list[str] | list[dict],
    ) -> ExamResult:
        specs = self._parse_required(required)
        tree = parse_code(code, language_id)
        detected = detect_concepts(tree, language_id, code)
        return grade(specs, detected)

    @property
    def exam_structure_ids(self) -> frozenset[str]:
        return get_exam_structure_ids()

    def validate_detected(
        self,
        detected: CoreDetectionResult,
        required: list[RequiredStructureSpec],
    ) -> ExamResult:
        return grade(required, detected)

    def missing_structure_labels(
        self,
        code: str,
        language_id: str,
        required: list[RequiredStructureSpec] | list[str] | list[dict],
    ) -> list[str]:
        missing = self.validate(code, language_id, required).missing
        if not missing:
            return []
        return [f"Отсутствует конструкция: {concept_label(item)}" for item in missing]

    def _parse_required(
        self,
        raw: list[RequiredStructureSpec] | list[str] | list[dict],
    ) -> list[RequiredStructureSpec]:
        allowed = get_exam_structure_ids()
        specs: list[RequiredStructureSpec] = []
        for item in raw:
            if isinstance(item, RequiredStructureSpec):
                if item.type in allowed:
                    specs.append(item)
                continue
            if isinstance(item, dict):
                type_id = map_required_type(str(item.get("type") or ""))
                if type_id in allowed:
                    specs.append(
                        RequiredStructureSpec(
                            type=type_id,
                            min_count=int(item.get("min_count") or 1),
                        )
                    )
                continue
            for type_id in normalize_construction_tags([str(item)]):
                specs.append(RequiredStructureSpec(type=type_id, min_count=1))
        return _dedupe_specs(specs)


def _dedupe_specs(specs: list[RequiredStructureSpec]) -> list[RequiredStructureSpec]:
    seen: set[str] = set()
    unique: list[RequiredStructureSpec] = []
    for spec in specs:
        if spec.type in seen:
            continue
        seen.add(spec.type)
        unique.append(spec)
    return unique
