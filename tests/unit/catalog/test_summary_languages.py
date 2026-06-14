from __future__ import annotations

from src.features.catalog.mappers import _summary_languages


def test_summary_languages__collects_translation_and_block_languages() -> None:
    assert _summary_languages(
        {
            "source_language": "python",
            "target_language": "pascal",
        }
    ) == ("pascal", "python")

    assert _summary_languages(
        {
            "language": "python",
            "blocks_by_language": {"pascal": [], "python": []},
        }
    ) == ("pascal", "python")
