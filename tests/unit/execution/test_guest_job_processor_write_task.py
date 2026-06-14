from __future__ import annotations

import pytest

from src.shared.execution.domain.execution_job import ExecutionJob
from src.shared.execution.services.guest_job_processor import GuestJobProcessor


def test_guest_job_processor__write_from_description_uses_translation_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeTranslationPipeline:
        def run(self, **kwargs: object) -> dict[str, object]:
            captured["task_type"] = str(kwargs.get("task_type"))
            return {"success": True, "test_results": [], "pattern_errors": []}

    processor = GuestJobProcessor()
    monkeypatch.setattr(processor, "_translation", lambda: FakeTranslationPipeline())

    job = ExecutionJob.create(
        user_id="guest:abc",
        language_id="python",
        code="for i in range(3):\n    print(i)",
        op="guest_full_check",
        task_id=4,
        payload={
            "task_snapshot": {
                "task_type": "task_write_from_description",
                "payload": {
                    "target_language": "python",
                    "test_cases": [{"inputs": "", "output": "0\n1\n2"}],
                },
            },
        },
    )

    result = processor.process(job)

    assert captured["task_type"] == "task_write_from_description"
    assert result["success"] is True
