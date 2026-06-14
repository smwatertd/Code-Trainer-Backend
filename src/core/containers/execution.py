from __future__ import annotations

from dependency_injector import containers, providers

from src.core.settings import AppSettings
from src.features.languages.services.language_registry import LanguageRegistry
from src.shared.execution.checking.code_runner_factory import create_code_runner
from src.shared.execution.checking.flow_validation_service import FlowValidationService
from src.shared.execution.pipeline.block_reorder_pipeline import BlockReorderPipeline
from src.shared.execution.pipeline.flowchart_pipeline import FlowchartPipeline
from src.shared.execution.pipeline.translation_pipeline import TranslationPipeline
from src.shared.execution.services.composite_job_processor import CompositeJobProcessor
from src.shared.execution.services.execution_service import ExecutionService
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.stores.memory_job_store import MemoryJobStore
from src.shared.execution.stores.redis_job_store import RedisJobStore


def _create_code_runner(settings: AppSettings, registry: LanguageRegistry):
    return create_code_runner(
        registry,
        prefer_docker=settings.execution.prefer_docker_runner,
        execution_settings=settings.execution,
    )


def _create_translation_pipeline(settings: AppSettings, registry: LanguageRegistry) -> TranslationPipeline:
    return TranslationPipeline(_create_code_runner(settings, registry))


def _create_block_reorder_pipeline(settings: AppSettings, registry: LanguageRegistry) -> BlockReorderPipeline:
    return BlockReorderPipeline(_create_code_runner(settings, registry))


def _create_flowchart_pipeline(settings: AppSettings, registry: LanguageRegistry) -> FlowchartPipeline:
    code_runner = _create_code_runner(settings, registry)
    return FlowchartPipeline(
        translation_pipeline=TranslationPipeline(code_runner),
        flow_validator=FlowValidationService(),
        code_runner=code_runner,
    )


def _create_job_store(settings: AppSettings, registry: LanguageRegistry) -> MemoryJobStore | RedisJobStore:
    if settings.execution.use_redis_store and settings.redis.url:
        return RedisJobStore(
            redis_url=settings.redis.url,
            settings=settings.execution,
            known_language_ids=registry.ids(),
        )
    return MemoryJobStore()


class ExecutionContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)
    registry = providers.Dependency(instance_of=LanguageRegistry)

    job_store = providers.Singleton(
        _create_job_store,
        settings=config,
        registry=registry,
    )

    translation_pipeline = providers.Singleton(
        _create_translation_pipeline,
        settings=config,
        registry=registry,
    )

    flowchart_pipeline = providers.Singleton(
        _create_flowchart_pipeline,
        settings=config,
        registry=registry,
    )

    block_reorder_pipeline = providers.Singleton(
        _create_block_reorder_pipeline,
        settings=config,
        registry=registry,
    )

    guest_job_processor = providers.Singleton(
        GuestJobProcessor,
        translation_pipeline=translation_pipeline,
        flowchart_pipeline=flowchart_pipeline,
        block_reorder_pipeline=block_reorder_pipeline,
    )

    job_processor = providers.Singleton(
        CompositeJobProcessor,
        guest_processor=guest_job_processor,
    )

    execution_service = providers.Singleton(
        ExecutionService,
        store=job_store,
        auto_process=providers.Callable(
            lambda settings: not settings.execution.use_redis_store,
            settings=config,
        ),
        processor=job_processor,
    )
