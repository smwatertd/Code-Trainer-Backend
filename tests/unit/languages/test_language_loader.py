from __future__ import annotations

import pytest

from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from tests.helpers.languages import LANGUAGES_DIR


def test_load_from_directory__returns_count_of_yaml_files() -> None:
    registry = LanguageRegistry()
    loader = LanguageLoader(registry)

    count = loader.load_from_directory(LANGUAGES_DIR)

    assert count == 5
    assert len(registry.all()) == 5


def test_reload__replaces_registry_contents() -> None:
    registry = LanguageRegistry()
    loader = LanguageLoader(registry)
    loader.load_from_directory(LANGUAGES_DIR)
    first_ids = set(registry.ids())

    loader.load_from_directory(LANGUAGES_DIR)

    assert set(registry.ids()) == first_ids


@pytest.mark.parametrize("language_id", ["python", "pascal", "java", "cpp", "csharp"])
def test_each_public_language_yaml__has_required_api_fields(language_id: str) -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(LANGUAGES_DIR)
    config = registry.get_or_raise(language_id)

    assert config.label
    assert config.file_extension.startswith(".")
    assert config.monaco_language
    assert config.supported_features


@pytest.mark.parametrize(
    ("language_id", "field", "expected_fragment"),
    [
        ("java", "local_one_shot", "${{class}}.java"),
        ("java", "docker_one_shot", "javac"),
        ("csharp", "docker_one_shot", "dotnet run"),
        ("pascal", "compile", "-o{binary}"),
    ],
)
def test_language_test_config__has_runner_fields(language_id: str, field: str, expected_fragment: str) -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(LANGUAGES_DIR)
    config = registry.get_or_raise(language_id)

    value = getattr(config.test, field, None)
    assert value is not None
    if isinstance(value, tuple):
        joined = " ".join(value)
        assert expected_fragment in joined
    else:
        assert expected_fragment in str(value)


def test_java_test_config__uses_one_shot_without_compile_steps() -> None:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(LANGUAGES_DIR)
    java = registry.get_or_raise("java")

    assert java.test.local_one_shot
    assert java.test.docker_one_shot
    assert java.test.compile is None
