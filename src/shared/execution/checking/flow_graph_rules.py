from __future__ import annotations

from collections import deque
from typing import Any

from src.shared.execution.checking.flow_student_messages import student_flow_error_text


def sequence_types_from_flow(
    flow: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
) -> list[str]:
    """Preserve student-authored block order when the editor sends a flow list."""
    if not flow:
        return []

    node_types = {str(node["id"]): str(node["type"]).strip().lower() for node in nodes}
    sequence: list[str] = []
    for step in flow:
        step_id = str(step.get("id") or "")
        block_type = str(step.get("type") or node_types.get(step_id) or "").strip().lower()
        if block_type:
            sequence.append(block_type)
    return sequence


def has_back_edge_to(
    anchor_id: str,
    adjacency: dict[str, list[str]],
    visited_ids: set[str],
) -> bool:
    descendants: set[str] = set()
    queue = deque(target for target in adjacency.get(anchor_id, []) if target in visited_ids and target != anchor_id)
    while queue:
        current = queue.popleft()
        if current == anchor_id or current in descendants:
            continue
        descendants.add(current)
        for target in adjacency.get(current, []):
            if target != anchor_id and target not in descendants:
                queue.append(target)

    return any(anchor_id in adjacency.get(source_id, []) for source_id in descendants)


def validate_loop_constructions(
    *,
    nodes: list[dict[str, Any]],
    adjacency: dict[str, list[str]],
    visited_ids: set[str],
    constructions: list[Any],
    require_loop_back_edge: bool,
) -> list[dict[str, str]]:
    tags = {str(item or "").strip().lower() for item in constructions if str(item or "").strip()}
    loop_tags = {"for_loop", "while_loop", "loop", "nested_loops"}
    if not require_loop_back_edge and not (tags & loop_tags):
        return []

    anchor_types = {"loop"}
    if tags & {"for_loop", "while_loop"}:
        anchor_types.add("decision")

    errors: list[dict[str, str]] = []
    anchored = False
    missing_back_edge = False
    for node in nodes:
        node_id = str(node["id"])
        if node_id not in visited_ids:
            continue
        if node["type"] not in anchor_types:
            continue
        anchored = True
        if not has_back_edge_to(node_id, adjacency, visited_ids):
            missing_back_edge = True

    if missing_back_edge:
        errors.append(
            {
                "type": "FLOW_LOOP_BACK_EDGE",
                "text": student_flow_error_text("FLOW_LOOP_BACK_EDGE"),
            }
        )

    if (tags & loop_tags) and not anchored:
        errors.append(
            {
                "type": "FLOW_CONSTRUCTION_MISSING",
                "text": student_flow_error_text("FLOW_CONSTRUCTION_MISSING"),
            }
        )

    return errors
