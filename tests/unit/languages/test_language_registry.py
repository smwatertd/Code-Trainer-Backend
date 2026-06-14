from __future__ import annotations

import pytest

from src.features.languages.domain.language_config import DockerConfig, LanguageConfig, LanguageFeature
from src.features.languages.services.language_registry import LanguageRegistry


def _python_config() -> LanguageConfig:
    return LanguageConfig(
        id="python",
        label="Python",
        file_extension=".py",
        monaco_language="python",
        supported_features=frozenset({LanguageFeature.COMPILE}),
        docker=DockerConfig(image="python_runner", compile="python -m py_compile {file}"),
    )


def test_register_and_get__is_case_insensitive() -> None:
    registry = LanguageRegistry()
    registry.register(_python_config())

    assert registry.get("PYTHON") is not None
    assert registry.get("python") is not None


def test_get_or_raise__lists_available_languages_in_error() -> None:
    registry = LanguageRegistry()
    registry.register(_python_config())

    with pytest.raises(ValueError, match="javascript") as exc_info:
        registry.get_or_raise("javascript")

    assert "python" in str(exc_info.value)


def test_clear__removes_all_languages() -> None:
    registry = LanguageRegistry()
    registry.register(_python_config())

    registry.clear()

    assert registry.is_loaded is False
    assert registry.all() == []


def test_ids__returns_registered_keys() -> None:
    registry = LanguageRegistry()
    registry.register(_python_config())
    registry.register(
        LanguageConfig(
            id="pascal",
            label="Pascal",
            file_extension=".pas",
            monaco_language="pascal",
            supported_features=frozenset({LanguageFeature.COMPILE}),
            docker=DockerConfig(image="pascal_runner", compile="fpc {file}"),
        )
    )

    assert sorted(registry.ids()) == ["pascal", "python"]
