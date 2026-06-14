from __future__ import annotations

from dependency_injector import containers, providers

from src.core.logger import LoguruLogger
from src.core.settings import AppSettings
from src.features.submissions.services.submission_result_persister import SubmissionResultPersister
from src.features.submissions.services.submissions_service import SubmissionsService
from src.features.submissions.usecases import (
    AbandonSubmissionUseCase,
    GetLatestPendingSubmissionUseCase,
    GetSubmissionUseCase,
    ListSubmissionHistoryUseCase,
    SubmitSubmissionUseCase,
)
from src.shared.execution.services.execution_rate_limiter import create_execution_rate_limiter


class SubmissionsContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=AppSettings)
    uow = providers.Dependency()
    catalog_service = providers.Dependency()
    execution_service = providers.Dependency()

    logger = providers.Singleton(LoguruLogger, name="submissions")

    execution_rate_limiter = providers.Singleton(
        create_execution_rate_limiter,
        settings=config.provided.execution,
        redis_url=config.provided.redis.url,
        use_redis=config.provided.execution.use_redis_store,
    )

    progress_service = providers.Dependency()
    curriculum_progress_service = providers.Dependency()

    result_persister = providers.Factory(
        SubmissionResultPersister,
        uow=uow,
        progress_service=progress_service,
        curriculum_progress_service=curriculum_progress_service,
    )

    submissions_service = providers.Factory(
        SubmissionsService,
        uow=uow,
        catalog_service=catalog_service,
        execution_service=execution_service,
        result_persister=result_persister,
        execution_settings=config.provided.execution,
        execution_rate_limiter=execution_rate_limiter,
    )

    get_submission_use_case = providers.Factory(
        GetSubmissionUseCase,
        submissions_service=submissions_service,
    )
    get_latest_pending_submission_use_case = providers.Factory(
        GetLatestPendingSubmissionUseCase,
        submissions_service=submissions_service,
    )
    submit_submission_use_case = providers.Factory(
        SubmitSubmissionUseCase,
        submissions_service=submissions_service,
    )
    abandon_submission_use_case = providers.Factory(
        AbandonSubmissionUseCase,
        submissions_service=submissions_service,
    )
    list_submission_history_use_case = providers.Factory(
        ListSubmissionHistoryUseCase,
        submissions_service=submissions_service,
    )
