from src.shared.execution.checking.flow_validation_service import FlowValidationService


def _node(node_id: str, node_type: str, *, x: float = 0, y: float = 0, text: str = "") -> dict:
    return {"id": node_id, "type": node_type, "text": text, "x": x, "y": y}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


def test_empty_flow_returns_flow_empty():
    service = FlowValidationService()
    result = service.validate_with_details(flow=[], flow_spec={})

    assert result["errors"][0]["type"] == "FLOW_EMPTY"
    assert result["execution_job_id"] is None
    assert result["semantic_checked"] is True


def test_valid_if_else_flowchart_passes_structural_check():
    service = FlowValidationService()
    nodes = [
        _node("1", "start", y=0),
        _node("2", "input", y=100),
        _node("3", "decision", y=200),
        _node("4", "output", y=300),
        _node("5", "output", y=400),
        _node("6", "end", y=500),
    ]
    edges = [
        _edge("1", "2"),
        _edge("2", "3"),
        _edge("3", "4"),
        _edge("3", "5"),
        _edge("4", "6"),
        _edge("5", "6"),
    ]
    flow_spec = {
        "required_sequence": ["start", "input", "decision", "output", "output", "end"],
    }
    task = {"constructions": ["if_statement"]}

    result = service.validate_with_details(
        flow=[],
        flow_spec=flow_spec,
        task=task,
        nodes=nodes,
        edges=edges,
    )

    assert result["errors"] == []
    assert result["execution_job_id"] is None


def test_missing_decision_for_if_statement_construction():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input"),
        _node("3", "output"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={},
        task={"constructions": ["if_statement"]},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_CONSTRUCTION_MISSING" for err in result["errors"])


def test_decision_without_two_branches_fails():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "decision"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={},
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_DECISION_BRANCHES" for err in result["errors"])


def test_disconnected_block_fails():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "end"),
        _node("3", "process", x=500),
    ]
    edges = [_edge("1", "2")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={},
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_DISCONNECTED" for err in result["errors"])


def test_required_sequence_mismatch():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={"required_sequence": ["start", "input", "decision", "end"]},
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_SEQUENCE_MISMATCH" for err in result["errors"])


def test_sequence_mismatch_is_student_safe_and_debug_keeps_expected_sequence():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={"required_sequence": ["start", "input", "decision", "end"]},
        task={},
        nodes=nodes,
        edges=edges,
    )

    mismatch = next(err for err in result["errors"] if err["type"] == "FLOW_SEQUENCE_MISMATCH")
    assert "→" not in mismatch["text"]
    assert "ожидаем" not in mismatch["text"].lower()
    assert "decision" not in mismatch["text"].lower()
    assert result["debug"]["expected_sequence"]
    assert "Условие" in result["debug"]["expected_sequence"]


def test_required_text_checks_pass():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input", text="readln(n)"),
        _node("3", "decision", text="n > 0 ?"),
        _node("4", "output", text="writeln('pos')"),
        _node("5", "output", text="writeln('nonpos')"),
        _node("6", "end"),
    ]
    edges = [
        _edge("1", "2"),
        _edge("2", "3"),
        _edge("3", "4"),
        _edge("3", "5"),
        _edge("4", "6"),
        _edge("5", "6"),
    ]

    result = service.validate_with_details(
        flow=[],
        flow_spec={
            "required_sequence": ["start", "input", "decision", "output", "output", "end"],
            "required_text_checks": [
                {"type": "input", "contains_any": ["readln", "n"]},
                {"type": "decision", "contains_any": ["> 0"]},
                {"type": "output", "contains_any": ["pos"]},
                {"type": "output", "contains_any": ["nonpos"]},
            ],
            "allow_extra_nodes": False,
        },
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert result["errors"] == []


def test_required_text_checks_fail():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input", text="readln(n)"),
        _node("3", "decision", text="n > 0 ?"),
        _node("4", "output", text="writeln('pos')"),
        _node("5", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4"), _edge("4", "5")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={
            "required_text_checks": [
                {"type": "output", "contains_any": ["nonpos"]},
            ],
        },
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_TEXT_MISMATCH" for err in result["errors"])


def test_text_mismatch_is_student_safe_and_debug_keeps_patterns():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "output", text="writeln('pos')"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={
            "required_text_checks": [
                {"type": "output", "contains_any": ["nonpos"]},
            ],
        },
        task={},
        nodes=nodes,
        edges=edges,
    )

    mismatch = next(err for err in result["errors"] if err["type"] == "FLOW_TEXT_MISMATCH")
    assert "nonpos" not in mismatch["text"].lower()
    assert "ожидаем" not in mismatch["text"].lower()
    assert result["debug"]["text_check_failures"][0]["patterns"] == ["nonpos"]


def test_construction_missing_is_student_safe_and_debug_keeps_details():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input"),
        _node("3", "output"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={},
        task={"constructions": ["if_statement"]},
        nodes=nodes,
        edges=edges,
    )

    missing = next(err for err in result["errors"] if err["type"] == "FLOW_CONSTRUCTION_MISSING")
    assert "ветвление" not in missing["text"].lower()
    assert result["debug"]["construction_missing"]
    assert "ветвление" in result["debug"]["construction_missing"][0]["missing"].lower()


def test_loop_back_edge_message_is_student_safe():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "loop"),
        _node("3", "process"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={"require_loop_back_edge": True},
        task={},
        nodes=nodes,
        edges=edges,
    )

    loop_err = next(err for err in result["errors"] if err["type"] == "FLOW_LOOP_BACK_EDGE")
    assert "следующей итерации" in loop_err["text"].lower()


def test_loop_without_back_edge_fails():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input", text="readln(n)"),
        _node("3", "process", text="s := 0"),
        _node("4", "loop", text="i := 1 to n"),
        _node("5", "process", text="s := s + i"),
        _node("6", "output", text="writeln(s)"),
        _node("7", "end"),
    ]
    edges = [
        _edge("1", "2"),
        _edge("2", "3"),
        _edge("3", "4"),
        _edge("4", "5"),
        _edge("5", "6"),
        _edge("6", "7"),
    ]

    result = service.validate_with_details(
        flow=[],
        flow_spec={"require_loop_back_edge": True},
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_LOOP_BACK_EDGE" for err in result["errors"])


def test_allow_extra_nodes_false_rejects_extra_block():
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "input"),
        _node("3", "process"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "4")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={
            "required_sequence": ["start", "input", "end"],
            "allow_extra_nodes": False,
        },
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_SEQUENCE_MISMATCH" for err in result["errors"])


def test_source_code_alignment_integrated_in_validation_service() -> None:
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "loop", text="for i in range(99)"),
        _node("3", "output", text="print(i)"),
        _node("4", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3"), _edge("3", "2"), _edge("2", "4")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={"require_loop_back_edge": True},
        task={"source_code": "for i in range(3):\n    print(i)"},
        nodes=nodes,
        edges=edges,
    )

    assert any(err["type"] == "FLOW_SOURCE_MISMATCH" for err in result["errors"])
    assert result["debug"]["source_alignment_failures"]


def test_source_code_alignment_skipped_when_source_missing() -> None:
    service = FlowValidationService()
    nodes = [
        _node("1", "start"),
        _node("2", "loop", text="for i in range(99)"),
        _node("3", "end"),
    ]
    edges = [_edge("1", "2"), _edge("2", "3")]

    result = service.validate_with_details(
        flow=[],
        flow_spec={},
        task={},
        nodes=nodes,
        edges=edges,
    )

    assert not any(err["type"] == "FLOW_SOURCE_MISMATCH" for err in result["errors"])
    assert "source_alignment_failures" not in result["debug"]
