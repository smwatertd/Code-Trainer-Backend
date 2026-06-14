from __future__ import annotations

from dependency_injector import containers, providers

from src.core.logger import LoguruLogger
from src.core.settings import AppSettings
from src.features.demo.services.demo_service import DemoService
from src.features.demo.services.guest_rate_limiter import create_guest_rate_limiter
from src.features.demo.usecases import GetDemoCheckResultUseCase, SubmitDemoCheckUseCase


class DemoContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)
    catalog_service = providers.Dependency()
    execution_service = providers.Dependency()

    logger = providers.Singleton(LoguruLogger, name="demo")

    guest_rate_limiter = providers.Singleton(
        create_guest_rate_limiter,
        guest_settings=config.provided.guest,
        redis_url=config.provided.redis.url,
        use_redis=config.provided.execution.use_redis_store,
    )

    demo_service = providers.Factory(
        DemoService,
        catalog_service=catalog_service,
        execution_service=execution_service,
        rate_limiter=guest_rate_limiter,
        guest_settings=config.provided.guest,
    )

    submit_demo_check_use_case = providers.Factory(
        SubmitDemoCheckUseCase,
        demo_service=demo_service,
    )

    get_demo_check_result_use_case = providers.Factory(
        GetDemoCheckResultUseCase,
        demo_service=demo_service,
    )
