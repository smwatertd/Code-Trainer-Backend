from __future__ import annotations

import time

from src.core.containers import Container
from src.core.logger import LoguruLogger
from src.features.demo.services.guest_rate_limiter import create_guest_rate_limiter
from src.shared.execution.services.composite_job_processor import CompositeJobProcessor
from src.shared.execution.services.execution_rate_limiter import create_execution_rate_limiter
from src.shared.execution.services.guest_job_processor import GuestJobProcessor
from src.shared.execution.services.submission_aware_worker_runner import SubmissionAwareWorkerRunner
from src.shared.execution.stores.redis_job_store import RedisJobStore


def run_worker(*, poll_interval: float | None = None) -> None:
    container = Container()
    settings = container.config()
    logger = LoguruLogger(name="execution_worker")

    if not settings.execution.use_redis_store or not settings.redis.url:
        raise RuntimeError("Worker requires EXECUTION__USE_REDIS_STORE=true and REDIS__URL")

    registry = container.languages.registry()
    store = RedisJobStore(
        redis_url=settings.redis.url,
        settings=settings.execution,
        known_language_ids=registry.ids(),
    )
    guest_limiter = create_guest_rate_limiter(
        guest_settings=settings.guest,
        redis_url=settings.redis.url,
        use_redis=True,
    )
    processor = CompositeJobProcessor(guest_processor=GuestJobProcessor())
    persister = container.submissions.result_persister()
    execution_rate_limiter = create_execution_rate_limiter(
        settings=settings.execution,
        redis_url=settings.redis.url,
        use_redis=True,
    )
    runner = SubmissionAwareWorkerRunner(
        store=store,
        processor=processor,
        persister=persister,
        execution_rate_limiter=execution_rate_limiter,
        guest_lifecycle=guest_limiter,
    )

    timeout = settings.execution.poll_timeout_seconds
    sleep_seconds = poll_interval if poll_interval is not None else 0.0
    worker_id = f"execution-worker@{settings.redis.url}"
    logger.info(f"Listening queues={store.list_queue_names()} worker={worker_id}")

    while True:
        processed = runner.process_next_blocking(timeout)
        if processed:
            logger.info("Processed one job")
        elif sleep_seconds > 0:
            time.sleep(sleep_seconds)


def main() -> None:
    run_worker()


if __name__ == "__main__":
    main()
