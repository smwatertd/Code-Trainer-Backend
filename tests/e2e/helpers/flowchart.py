from __future__ import annotations

from tests.fixtures.flowchart_sample_tasks import flowchart_test_id

FC_IF_ELSE = flowchart_test_id(3)
FC_HELLO = flowchart_test_id(6)
FC_FOR_LOOP = flowchart_test_id(40)


def valid_if_flowchart() -> tuple[list[dict], list[dict]]:
    nodes = [
        {"id": "1", "type": "start", "x": 0, "y": 0, "text": ""},
        {"id": "2", "type": "input", "x": 0, "y": 100, "text": "readln(n)"},
        {"id": "3", "type": "decision", "x": 0, "y": 200, "text": "n > 0 ?"},
        {"id": "4", "type": "output", "x": 0, "y": 300, "text": "writeln('pos')"},
        {"id": "5", "type": "output", "x": 0, "y": 400, "text": "writeln('nonpos')"},
        {"id": "6", "type": "end", "x": 0, "y": 500, "text": ""},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "4"},
        {"source": "3", "target": "5"},
        {"source": "4", "target": "6"},
        {"source": "5", "target": "6"},
    ]
    return nodes, edges


def hello_flowchart() -> tuple[list[dict], list[dict]]:
    nodes = [
        {"id": "1", "type": "start", "x": 0, "y": 0},
        {"id": "2", "type": "output", "x": 0, "y": 100, "text": "print('hello')"},
        {"id": "3", "type": "end", "x": 0, "y": 200},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
    ]
    return nodes, edges
