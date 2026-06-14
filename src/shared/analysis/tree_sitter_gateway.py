"""Tree-sitter parser access via language registry.

Provides a shim layer so callers use the classic tree-sitter property API
(node.type, node.children, node.text, tree.root_node) regardless of whether
tree-sitter ≥0.22 (method-based API) or the older property-based API is installed.
"""

from __future__ import annotations

from tree_sitter_language_pack import get_parser

from src.shared.analysis._language_grammar import get_tree_sitter_grammar


class _CompatNode:
    """Wraps tree-sitter Node across property-based and method-based APIs."""

    __slots__ = ("_n", "_src")

    def __init__(self, node: object, src: bytes) -> None:
        self._n = node
        self._src = src

    @staticmethod
    def _read_attr(node: object, *names: str) -> object | None:
        for name in names:
            if hasattr(node, name):
                value = getattr(node, name)
                return value() if callable(value) else value
        return None

    @property
    def type(self) -> str:
        value = self._read_attr(self._n, "type", "kind")
        return str(value or "")

    @property
    def children(self) -> list[_CompatNode]:
        raw_children = self._read_attr(self._n, "children")
        if isinstance(raw_children, list):
            return [_CompatNode(child, self._src) for child in raw_children]

        child_count = self._read_attr(self._n, "child_count")
        if child_count is None:
            return []
        return [_CompatNode(self._n.child(i), self._src) for i in range(int(child_count))]  # type: ignore[attr-defined]

    @property
    def text(self) -> bytes:
        raw = self._read_attr(self._n, "text")
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw)
        start = self._read_attr(self._n, "start_byte")
        end = self._read_attr(self._n, "end_byte")
        if start is not None and end is not None:
            return self._src[int(start) : int(end)]
        return b""

    @property
    def parent(self) -> _CompatNode | None:
        raw = self._read_attr(self._n, "parent")
        return _CompatNode(raw, self._src) if raw is not None else None

    def child_by_field_name(self, name: str) -> _CompatNode | None:
        if not hasattr(self._n, "child_by_field_name"):
            return None
        child = self._n.child_by_field_name(name)  # type: ignore[attr-defined]
        return _CompatNode(child, self._src) if child is not None else None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _CompatNode):
            start = self._read_attr(self._n, "start_byte")
            end = self._read_attr(self._n, "end_byte")
            other_start = other._read_attr(other._n, "start_byte")
            other_end = other._read_attr(other._n, "end_byte")
            return start == other_start and end == other_end
        return NotImplemented

    def __hash__(self) -> int:
        start = self._read_attr(self._n, "start_byte")
        end = self._read_attr(self._n, "end_byte")
        return hash((start, end))

    def __bool__(self) -> bool:
        return self._n is not None


class _CompatTree:
    """Wraps a tree-sitter 0.25+ Tree to expose the classic property API."""

    __slots__ = ("_t", "_src")

    def __init__(self, tree: object, src: bytes) -> None:
        self._t = tree
        self._src = src

    @property
    def root_node(self) -> _CompatNode:
        raw = _CompatNode._read_attr(self._t, "root_node")
        if raw is None:
            raise RuntimeError("Tree-sitter tree has no root node")
        return _CompatNode(raw, self._src)


def parse_code(code: str, language_id: str) -> _CompatTree:
    grammar = get_tree_sitter_grammar(language_id)

    parser = get_parser(grammar)
    src = code.encode("utf-8")
    try:
        raw_tree = parser.parse(code)
    except TypeError:
        raw_tree = parser.parse(src)
    return _CompatTree(raw_tree, src)
