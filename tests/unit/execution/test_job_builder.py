from __future__ import annotations

from src.shared.execution.services.job_builder import build_dedup_key


def test_job_builder__same_payload_produces_same_key() -> None:
    payload = {"guest": True, "client_ip": "1.2.3.4"}

    first = build_dedup_key(
        user_id="guest:1.2.3.4",
        task_id=2,
        code="print(1)",
        op="guest_full_check",
        language_id="python",
        payload=payload,
    )
    second = build_dedup_key(
        user_id="guest:1.2.3.4",
        task_id=2,
        code="print(1)",
        op="guest_full_check",
        language_id="python",
        payload={"client_ip": "1.2.3.4", "guest": True},
    )

    assert first == second


def test_job_builder__different_code_changes_key() -> None:
    base_kwargs = {
        "user_id": "guest:1.2.3.4",
        "task_id": 2,
        "op": "guest_full_check",
        "language_id": "python",
        "payload": {"guest": True},
    }

    first = build_dedup_key(code="print(1)", **base_kwargs)
    second = build_dedup_key(code="print(2)", **base_kwargs)

    assert first != second


def test_job_builder__submission_op_uses_submission_id() -> None:
    key = build_dedup_key(
        user_id="42",
        task_id=2,
        code="print(1)",
        op="process_submission",
        language_id="python",
        payload={"submission_id": 99},
    )

    assert key == "submission:99:process_submission"


def test_job_builder__submission_op_without_id_falls_back_to_hash() -> None:
    key = build_dedup_key(
        user_id="42",
        task_id=2,
        code="print(1)",
        op="process_submission",
        language_id="python",
        payload={"submission_id": None},
    )

    assert not key.startswith("submission:")
