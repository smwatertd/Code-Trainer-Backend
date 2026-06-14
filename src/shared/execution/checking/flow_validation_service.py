from __future__ import annotations

from collections import deque
from typing import Any

from src.shared.execution.checking.flow_block_constructions import (
    DEFAULT_ALLOWED_BLOCKS,
    format_sequence_labels,
    label_block_type,
    validate_constructions_from_blocks,
)
from src.shared.execution.checking.flow_graph_rules import (
    sequence_types_from_flow,
    validate_loop_constructions,
)
from src.shared.execution.checking.flow_source_alignment import (
    block_text_for_matching,
    expand_block_text_aliases,
    normalize_flow_text,
    validate_flowchart_source_alignment,
)
from src.shared.execution.checking.flow_student_messages import student_flow_error_text


class FlowValidationService:
    """Validates student-built flowcharts by block types and graph structure only."""

    def validate_with_details(
        self,
        flow: list[dict[str, Any]],
        flow_spec: dict[str, Any],
        task: dict[str, Any] | None = None,
        nodes: list[dict[str, Any]] | None = None,
        edges: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        errors: list[dict[str, str]] = []

        allowed_blocks = set(flow_spec.get("allowed_blocks") or DEFAULT_ALLOWED_BLOCKS)
        required_sequence = [
            str(item).strip().lower() for item in (flow_spec.get("required_sequence") or []) if str(item).strip()
        ]

        normalized_nodes = self._normalize_nodes(nodes or flow)
        if not normalized_nodes:
            return self._structural_result(
                [
                    {
                        "type": "FLOW_EMPTY",
                        "text": "Добавьте блоки в схему перед проверкой.",
                    }
                ],
                debug={
                    "node_count": 0,
                    "edge_count": len(edges or []),
                    "submitted_types": [],
                    "reachable_types": [],
                    "detected_sequence": "",
                    "expected_sequence": format_sequence_labels(required_sequence) if required_sequence else "",
                    "visited_node_count": 0,
                    "disconnected_node_count": 0,
                    "error_types": ["FLOW_EMPTY"],
                    "used_nodes_source": "nodes" if nodes else "flow",
                },
            )

        if allowed_blocks:
            for index, node in enumerate(normalized_nodes, start=1):
                if node["type"] not in allowed_blocks:
                    errors.append(
                        {
                            "type": "FLOW_BLOCK_UNSUPPORTED",
                            "text": (
                                f"Блок #{index} имеет неподдерживаемый тип: " f"«{label_block_type(node['type'])}»."
                            ),
                        }
                    )

        submitted_types = [node["type"] for node in normalized_nodes]

        if "start" in allowed_blocks and "start" not in submitted_types:
            errors.append(
                {
                    "type": "FLOW_START_MISSING",
                    "text": "Схема должна содержать блок «Начало».",
                }
            )

        if "end" in allowed_blocks and "end" not in submitted_types:
            errors.append(
                {
                    "type": "FLOW_END_MISSING",
                    "text": "Схема должна содержать блок «Конец».",
                }
            )

        reachable_sequence = normalized_nodes
        reachable_types = submitted_types
        adjacency: dict[str, list[str]] = {}
        visited_ids: set[str] = set()

        if nodes and edges is not None:
            graph_errors, reachable_sequence, adjacency, visited_ids = self._validate_graph(normalized_nodes, edges)
            errors.extend(graph_errors)
            reachable_types = [node["type"] for node in reachable_sequence]
            errors.extend(
                self._validate_graph_topology(
                    nodes=reachable_sequence,
                    adjacency=adjacency,
                    visited_ids=visited_ids,
                )
            )
        elif required_sequence:
            reachable_types = submitted_types

        flow_sequence = sequence_types_from_flow(flow, normalized_nodes)
        sequence_for_checks = (
            flow_sequence
            if flow_sequence
            else submitted_types if flow_spec.get("allow_extra_nodes") is not False else reachable_types
        )

        has_loop_block = any(node["type"] == "loop" for node in (reachable_sequence or normalized_nodes))
        use_subsequence = flow_spec.get("allow_extra_nodes") is not False or has_loop_block

        if required_sequence:
            if use_subsequence:
                if not self._contains_subsequence(sequence_for_checks, required_sequence):
                    errors.append(
                        {
                            "type": "FLOW_SEQUENCE_MISMATCH",
                            "text": student_flow_error_text("FLOW_SEQUENCE_MISMATCH"),
                        }
                    )
            elif sequence_for_checks != required_sequence:
                errors.append(
                    {
                        "type": "FLOW_SEQUENCE_MISMATCH",
                        "text": student_flow_error_text("FLOW_SEQUENCE_MISMATCH"),
                    }
                )

        text_checks = flow_spec.get("required_text_checks") or []
        text_check_failures: list[dict[str, Any]] = []
        if text_checks:
            text_errors, text_check_failures = self._validate_required_text_checks(reachable_sequence, text_checks)
            errors.extend(text_errors)

        source_code = str((task or {}).get("source_code") or "").strip()
        source_alignment_failures: list[dict[str, Any]] = []
        if source_code:
            alignment_errors, source_alignment_failures = validate_flowchart_source_alignment(
                reachable_sequence,
                source_code,
            )
            errors.extend(alignment_errors)

        task_constructions = list((task or {}).get("constructions") or [])
        if nodes and edges is not None:
            errors.extend(
                validate_loop_constructions(
                    nodes=reachable_sequence,
                    adjacency=adjacency,
                    visited_ids=visited_ids,
                    constructions=task_constructions,
                    require_loop_back_edge=bool(flow_spec.get("require_loop_back_edge")),
                )
            )
        construction_errors, construction_debug = validate_constructions_from_blocks(
            submitted_types=reachable_types,
            constructions=task_constructions,
        )
        errors.extend(construction_errors)

        debug = self._build_debug_info(
            normalized_nodes=normalized_nodes,
            edges=edges or [],
            reachable_sequence=reachable_sequence,
            reachable_types=reachable_types,
            submitted_types=submitted_types,
            sequence_for_checks=sequence_for_checks,
            visited_ids=visited_ids,
            errors=errors,
            required_sequence=required_sequence,
            used_nodes_source="nodes" if nodes else "flow",
            text_check_failures=text_check_failures,
            source_alignment_failures=source_alignment_failures,
            construction_missing=construction_debug,
        )
        return self._structural_result(errors, debug=debug)

    @staticmethod
    def _build_debug_info(
        *,
        normalized_nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        reachable_sequence: list[dict[str, Any]],
        reachable_types: list[str],
        submitted_types: list[str],
        sequence_for_checks: list[str],
        visited_ids: set[str],
        errors: list[dict[str, str]],
        required_sequence: list[str],
        used_nodes_source: str,
        text_check_failures: list[dict[str, Any]] | None = None,
        source_alignment_failures: list[dict[str, Any]] | None = None,
        construction_missing: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        detected_labels = [label_block_type(item) for item in sequence_for_checks or reachable_types]
        debug: dict[str, Any] = {
            "node_count": len(normalized_nodes),
            "edge_count": len(edges),
            "submitted_types": submitted_types,
            "reachable_types": reachable_types,
            "sequence_for_checks": sequence_for_checks,
            "detected_sequence": " → ".join(detected_labels) if detected_labels else "",
            "expected_sequence": format_sequence_labels(required_sequence) if required_sequence else "",
            "visited_node_count": len(visited_ids),
            "disconnected_node_count": max(0, len(normalized_nodes) - len(visited_ids)),
            "error_types": [item["type"] for item in errors],
            "used_nodes_source": used_nodes_source,
        }
        if text_check_failures:
            debug["text_check_failures"] = text_check_failures
        if source_alignment_failures:
            debug["source_alignment_failures"] = source_alignment_failures
        if construction_missing:
            debug["construction_missing"] = construction_missing
        return debug

    @staticmethod
    def _structural_result(
        errors: list[dict[str, str]],
        debug: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "errors": errors,
            "execution_results": [],
            "test_cases": [],
            "semantic_checked": True,
            "execution_job_id": None,
            "status": None,
            "debug": debug,
        }

    def validate(
        self,
        flow: list[dict[str, Any]],
        flow_spec: dict[str, Any],
        task: dict[str, Any] | None = None,
        nodes: list[dict[str, Any]] | None = None,
        edges: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, str]]:
        details = self.validate_with_details(
            flow=flow,
            flow_spec=flow_spec,
            task=task,
            nodes=nodes,
            edges=edges,
        )
        return details["errors"]

    @staticmethod
    def _serialize_execution_results(
        execution_results: list[Any],
    ) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for index, item in enumerate(execution_results, start=1):
            serialized.append(
                {
                    "case": getattr(item, "case", index),
                    "status": getattr(item, "status", "ERROR"),
                    "inputs": getattr(item, "inputs", ""),
                    "expected": getattr(item, "expected", ""),
                    "actual": getattr(item, "actual", ""),
                    "message": getattr(item, "message", ""),
                }
            )
        return serialized

    def _validate_graph(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> tuple[
        list[dict[str, str]],
        list[dict[str, Any]],
        dict[str, list[str]],
        set[str],
    ]:
        errors: list[dict[str, str]] = []
        node_by_id = {str(node["id"]): node for node in nodes}
        adjacency: dict[str, list[str]] = {str(node["id"]): [] for node in nodes}

        for edge in edges:
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if source in adjacency and target in node_by_id:
                adjacency[source].append(target)

        start_nodes = [node for node in nodes if node["type"] == "start"]
        if not start_nodes:
            return errors, [], adjacency, set()

        start_id = str(start_nodes[0]["id"])
        queue = deque([start_id])
        visited: set[str] = set()
        distances: dict[str, int] = {start_id: 0}

        def _neighbor_order(node_id: str, neighbors: list[str]) -> list[str]:
            node_type = node_by_id.get(node_id, {}).get("type")
            if node_type in {"loop", "decision"}:
                return sorted(
                    neighbors,
                    key=lambda target_id: (
                        1 if node_by_id.get(target_id, {}).get("type") == "end" else 0,
                        distances.get(target_id, 10**9),
                        target_id,
                    ),
                )
            return neighbors

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for target in _neighbor_order(current, adjacency.get(current, [])):
                if target not in distances:
                    distances[target] = distances[current] + 1
                if target not in visited:
                    queue.append(target)

        disconnected = [node for node in nodes if str(node["id"]) not in visited]
        if disconnected:
            labels = ", ".join(label_block_type(node["type"]) for node in disconnected)
            errors.append(
                {
                    "type": "FLOW_DISCONNECTED",
                    "text": f"Есть несоединённые блоки: {labels}.",
                }
            )

        reachable_ids = visited
        has_loop = any(node["type"] == "loop" for node in nodes if str(node["id"]) in reachable_ids)
        if has_loop:
            reachable_nodes = self._execution_order_for_loops(
                nodes=nodes,
                adjacency=adjacency,
                start_id=start_id,
                visited_ids=reachable_ids,
            )
        else:
            reachable_nodes = [node for node in nodes if str(node["id"]) in reachable_ids]
            reachable_nodes.sort(
                key=lambda node: (
                    distances.get(str(node["id"]), 10**9),
                    float(node["x"]),
                    float(node["y"]),
                    str(node["id"]),
                )
            )
        return errors, reachable_nodes, adjacency, visited

    @staticmethod
    def _execution_order_for_loops(
        *,
        nodes: list[dict[str, Any]],
        adjacency: dict[str, list[str]],
        start_id: str,
        visited_ids: set[str],
    ) -> list[dict[str, Any]]:
        """Order nodes for loop schemes: traverse body before exiting to «Конец»."""
        node_by_id = {str(node["id"]): node for node in nodes}
        ordered_ids: list[str] = []
        walk_visited: set[str] = set()

        def walk(node_id: str) -> None:
            if node_id in walk_visited or node_id not in visited_ids:
                return
            walk_visited.add(node_id)
            ordered_ids.append(node_id)
            node = node_by_id.get(node_id)
            if not node:
                return
            neighbors = adjacency.get(node_id, [])
            if node["type"] == "loop":
                body = [target for target in neighbors if node_by_id.get(target, {}).get("type") != "end"]
                exits = [target for target in neighbors if node_by_id.get(target, {}).get("type") == "end"]
                for target in body:
                    walk(target)
                for target in exits:
                    walk(target)
                return
            for target in neighbors:
                walk(target)

        walk(start_id)
        return [node_by_id[node_id] for node_id in ordered_ids if node_id in node_by_id]

    def _validate_graph_topology(
        self,
        *,
        nodes: list[dict[str, Any]],
        adjacency: dict[str, list[str]],
        visited_ids: set[str],
    ) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        end_reachable = any(node["type"] == "end" and str(node["id"]) in visited_ids for node in nodes)
        if any(node["type"] == "end" for node in nodes) and not end_reachable:
            errors.append(
                {
                    "type": "FLOW_END_UNREACHABLE",
                    "text": "Блок «Конец» не связан со стартом — проверьте стрелки.",
                }
            )

        for node in nodes:
            node_id = str(node["id"])
            if node_id not in visited_ids:
                continue

            outgoing = adjacency.get(node_id, [])
            node_type = node["type"]

            if node_type == "decision" and len(outgoing) < 2:
                errors.append(
                    {
                        "type": "FLOW_DECISION_BRANCHES",
                        "text": ("У блока «Условие» должно быть две ветви " "(да и нет)."),
                    }
                )

            if node_type != "end" and not outgoing:
                errors.append(
                    {
                        "type": "FLOW_DEAD_END",
                        "text": (
                            f"Блок «{label_block_type(node_type)}» не ведёт "
                            "дальше — добавьте стрелку к следующему блоку."
                        ),
                    }
                )

        return errors

    def _validate_required_text_checks(
        self,
        nodes: list[dict[str, Any]],
        text_checks: list[Any],
    ) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        errors: list[dict[str, str]] = []
        failures: list[dict[str, Any]] = []
        matched_ids: set[str] = set()

        for raw in text_checks:
            if not isinstance(raw, dict):
                continue
            node_type = str(raw.get("type") or "").strip().lower()
            patterns = [
                normalize_flow_text(str(item))
                for item in (raw.get("contains_any") or raw.get("text_patterns") or [])
                if str(item).strip()
            ]
            if not node_type or not patterns:
                continue

            matched = False
            for node in nodes:
                node_id = str(node["id"])
                if node_id in matched_ids or node["type"] != node_type:
                    continue
                expanded = expand_block_text_aliases(block_text_for_matching(str(node.get("text") or "")))
                if any(pattern in expanded for pattern in patterns):
                    matched_ids.add(node_id)
                    matched = True
                    break

            if not matched:
                errors.append(
                    {
                        "type": "FLOW_TEXT_MISMATCH",
                        "text": student_flow_error_text("FLOW_TEXT_MISMATCH"),
                    }
                )
                failures.append(
                    {
                        "block_type": node_type,
                        "patterns": patterns,
                    }
                )

        return errors, failures

    def _validate_loop_back_edges(
        self,
        *,
        nodes: list[dict[str, Any]],
        adjacency: dict[str, list[str]],
        visited_ids: set[str],
    ) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []

        for node in nodes:
            if node["type"] != "loop":
                continue
            loop_id = str(node["id"])
            if loop_id not in visited_ids:
                continue

            if not self._has_loop_back_edge(loop_id, adjacency, visited_ids):
                errors.append(
                    {
                        "type": "FLOW_LOOP_BACK_EDGE",
                        "text": student_flow_error_text("FLOW_LOOP_BACK_EDGE"),
                    }
                )

        return errors

    @staticmethod
    def _has_loop_back_edge(
        loop_id: str,
        adjacency: dict[str, list[str]],
        visited_ids: set[str],
    ) -> bool:
        descendants: set[str] = set()
        queue = deque(target for target in adjacency.get(loop_id, []) if target in visited_ids and target != loop_id)
        while queue:
            current = queue.popleft()
            if current == loop_id or current in descendants:
                continue
            descendants.add(current)
            for target in adjacency.get(current, []):
                if target != loop_id and target not in descendants:
                    queue.append(target)

        return any(loop_id in adjacency.get(source_id, []) for source_id in descendants)

    @staticmethod
    def _normalize_nodes(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(items, start=1):
            position = item.get("position") or {}
            normalized.append(
                {
                    "id": str(item.get("id") or index),
                    "type": FlowValidationService._normalize_block_type(item),
                    "text": str(item.get("text") or item.get("label") or "").strip(),
                    "x": position.get("x", item.get("x", index * 100)),
                    "y": position.get("y", item.get("y", 0)),
                }
            )
        return normalized

    @staticmethod
    def _normalize_block_type(item: dict[str, Any]) -> str:
        raw = item.get("type") or item.get("label") or ""
        return str(raw).strip().lower()

    @staticmethod
    def _contains_subsequence(submitted: list[str], expected: list[str]) -> bool:
        if not expected:
            return True

        pos = 0
        for block_type in submitted:
            if block_type == expected[pos]:
                pos += 1
                if pos == len(expected):
                    return True
        return False
