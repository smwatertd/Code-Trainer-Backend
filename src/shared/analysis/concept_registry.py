from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_CONCEPTS_PATH = Path(__file__).resolve().parents[3] / "resources" / "concepts.yml"


@lru_cache
def load_concepts() -> dict[str, dict]:
    try:
        with _CONCEPTS_PATH.open(encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except OSError:
        return {}


def get_concept(concept_id: str) -> dict | None:
    return load_concepts().get(concept_id)
