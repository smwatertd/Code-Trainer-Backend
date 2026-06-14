from __future__ import annotations

from src.shared.analysis.domain.constructions import CONCEPT_IDS, CONSTRUCTION_TO_CONCEPTS


def get_exam_structure_ids() -> frozenset[str]:
    return CONCEPT_IDS


def map_required_type(name: str) -> str:
    concepts = _concepts_for_tag(name)
    if len(concepts) == 1:
        return concepts[0]
    return str(name or "").strip().lower()


def normalize_construction_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in tags:
        for concept_id in _concepts_for_tag(str(raw or "")):
            if concept_id not in seen:
                seen.add(concept_id)
                ordered.append(concept_id)
    return ordered


def _concepts_for_tag(tag: str) -> list[str]:
    normalized = str(tag or "").strip().lower()
    if not normalized:
        return []
    if normalized in CONCEPT_IDS:
        return [normalized]
    return [concept_id for concept_id in CONSTRUCTION_TO_CONCEPTS.get(normalized, ()) if concept_id in CONCEPT_IDS]
