from __future__ import annotations

from typing import Any

from src.features.tasks.domain.enums import TaskFamily, task_family_from_legacy_type
from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.interfaces.job_processor import JobProcessor
from src.shared.execution.pipeline.block_reorder_pipeline import BlockReorderPipeline
from src.shared.execution.pipeline.bootstrap import (
    get_default_block_reorder_pipeline,
    get_default_flowchart_pipeline,
    get_default_translation_pipeline,
)
from src.shared.execution.pipeline.flowchart_pipeline import FlowchartPipeline
from src.shared.execution.pipeline.translation_pipeline import TranslationPipeline


class GuestJobProcessor(JobProcessor):
    def __init__(
        self,
        translation_pipeline: TranslationPipeline | None = None,
        flowchart_pipeline: FlowchartPipeline | None = None,
        block_reorder_pipeline: BlockReorderPipeline | None = None,
    ) -> None:
        self._translation_pipeline = translation_pipeline
        self._flowchart_pipeline = flowchart_pipeline
        self._block_reorder_pipeline = block_reorder_pipeline

    def process(self, job: ExecutionJob) -> dict[str, object]:
        task = (job.payload or {}).get("task_snapshot")
        if not task:
            return {
                "success": False,
                "compiler_errors": [{"type": "INTERNAL", "text": "Task snapshot missing"}],
            }

        family = task_family_from_legacy_type(str(task.get("task_type", "")))
        if family is TaskFamily.BLOCK_REORDER:
            return self._process_block_reorder(job, task)
        if family is TaskFamily.TRANSLATION:
            return self._process_translation(job, task)
        if family is TaskFamily.FLOWCHART:
            return self._process_flowchart(job, task)

        return {
            "success": False,
            "compiler_errors": [
                {"type": "UNSUPPORTED", "text": f"Unsupported task type: {task.get('task_type')}"},
            ],
        }

    def _translation(self) -> TranslationPipeline:
        return self._translation_pipeline or get_default_translation_pipeline()

    def _flowchart(self) -> FlowchartPipeline:
        return self._flowchart_pipeline or get_default_flowchart_pipeline()

    def _process_translation(self, job: ExecutionJob, task: dict[str, Any]) -> dict[str, object]:
        payload = task.get("payload") or {}
        return self._translation().run(
            language_id=job.language_id,
            code=job.code,
            task_type=str(task.get("task_type") or "translation"),
            task_payload=payload,
            mode="full",
        )

    def _process_flowchart(self, job: ExecutionJob, task: dict[str, Any]) -> dict[str, object]:
        payload = task.get("payload") or {}
        return self._flowchart().run(
            language_id=job.language_id,
            code=job.code,
            task_type=str(task.get("task_type") or "task_flowchart_to_code"),
            task_payload=payload,
            job_payload=job.payload or {},
        )

    def _block_reorder(self) -> BlockReorderPipeline:
        return self._block_reorder_pipeline or get_default_block_reorder_pipeline()

    def _process_block_reorder(self, job: ExecutionJob, task: dict[str, Any]) -> dict[str, object]:
        payload = task.get("payload") or {}
        block_order = list(job.payload.get("block_order") or [])
        return self._block_reorder().run(
            language_id=job.language_id,
            code=job.code,
            task_payload=payload,
            block_order=block_order,
        )
