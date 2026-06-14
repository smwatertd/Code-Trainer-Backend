from __future__ import annotations

from functools import lru_cache

from src.core.settings import get_settings
from src.features.languages.services.language_loader import LanguageLoader
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.code_runner_factory import create_code_runner
from src.shared.execution.checking.flow_validation_service import FlowValidationService
from src.shared.execution.pipeline.block_reorder_pipeline import BlockReorderPipeline
from src.shared.execution.pipeline.flowchart_pipeline import FlowchartPipeline
from src.shared.execution.pipeline.translation_pipeline import TranslationPipeline


@lru_cache
def get_default_translation_pipeline() -> TranslationPipeline:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(get_settings().languages_dir)
    return TranslationPipeline(create_code_runner(registry))


@lru_cache
def get_default_block_reorder_pipeline() -> BlockReorderPipeline:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(get_settings().languages_dir)
    return BlockReorderPipeline(create_code_runner(registry))


@lru_cache
def get_default_flowchart_pipeline() -> FlowchartPipeline:
    registry = LanguageRegistry()
    LanguageLoader(registry).load_from_directory(get_settings().languages_dir)
    code_runner = create_code_runner(registry)
    return FlowchartPipeline(
        translation_pipeline=TranslationPipeline(code_runner),
        flow_validator=FlowValidationService(),
        code_runner=code_runner,
    )
