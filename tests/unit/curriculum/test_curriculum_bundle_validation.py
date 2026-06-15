from __future__ import annotations

from pathlib import Path

import pytest

from src.shared.curriculum.loader import load_curriculum_link_bundle, validate_curriculum_link_bundle

_CURRICULUM_ROOT = Path(__file__).resolve().parents[3] / "resources" / "curriculum"


def test_validate_curriculum_link_bundle__python_is_valid() -> None:
    bundle = load_curriculum_link_bundle(_CURRICULUM_ROOT, "python", force=True)

    errors = validate_curriculum_link_bundle(bundle)

    assert errors == []


def test_validate_curriculum_link_bundle__pascal_is_valid() -> None:
    bundle = load_curriculum_link_bundle(_CURRICULUM_ROOT, "pascal", force=True)

    errors = validate_curriculum_link_bundle(bundle)

    assert errors == []


@pytest.mark.parametrize("language", ["cpp", "java", "csharp"])
def test_validate_curriculum_link_bundle__c_family_tracks_are_valid(language: str) -> None:
    bundle = load_curriculum_link_bundle(_CURRICULUM_ROOT, language, force=True)

    errors = validate_curriculum_link_bundle(bundle)

    assert errors == []
