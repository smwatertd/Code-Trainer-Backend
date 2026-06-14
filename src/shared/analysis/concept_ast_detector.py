"""Concept presence detection via concepts.yml ast_nodes + narrow special rules."""

from __future__ import annotations

import re
from collections import Counter

from src.shared.analysis.concept_registry import get_concept, load_concepts
from src.shared.analysis.domain.constructions import CONCEPT_IDS
from src.shared.analysis.domain.core_detection import CoreDetectionResult
from src.shared.analysis.tree_sitter_gateway import _CompatNode as Node
from src.shared.analysis.tree_sitter_gateway import _CompatTree as Tree

_INVOKE_NODE_TYPES: dict[str, tuple[str, ...]] = {
    "python": ("call",),
    "javascript": ("call_expression",),
    "java": ("method_invocation",),
    "cpp": ("call_expression",),
    "csharp": ("invocation_expression",),
}

_LOOP_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({"for_statement", "while_statement"}),
    "javascript": frozenset(
        {"for_statement", "while_statement", "for_in_statement", "for_of_statement", "do_statement"}
    ),
    "java": frozenset({"for_statement", "while_statement", "do_statement", "enhanced_for_statement"}),
    "cpp": frozenset({"for_statement", "while_statement", "do_statement", "range_based_for_statement"}),
    "csharp": frozenset({"for_statement", "while_statement", "do_statement", "foreach_statement"}),
    "pascal": frozenset({"for", "kFor", "while", "kWhile"}),
}

_AMBIGUOUS_CONCEPTS = frozenset(
    {
        "recursion",
        "map",
        "filter",
        "reduce",
        "sort",
        "file_io",
        "comprehension",
        "io",
        "nested_loops",
    }
)

_TEXT_PATTERNS: dict[str, dict[str, re.Pattern[str]]] = {
    "map": {
        "python": re.compile(r"(?<![.\w])map\s*\(|\.map\s*\(", re.I),
        "javascript": re.compile(r"\.map\s*\(", re.I),
        "java": re.compile(r"\.map\s*\(", re.I),
        "cpp": re.compile(r"std::transform\s*\(", re.I),
        "csharp": re.compile(r"\.Select\s*\(", re.I),
    },
    "filter": {
        "python": re.compile(r"(?<![.\w])filter\s*\(|\.filter\s*\(", re.I),
        "javascript": re.compile(r"\.filter\s*\(", re.I),
        "java": re.compile(r"\.filter\s*\(", re.I),
        "cpp": re.compile(r"std::copy_if\s*\(", re.I),
        "csharp": re.compile(r"\.Where\s*\(", re.I),
    },
    "reduce": {
        "python": re.compile(r"(?<![.\w])reduce\s*\(|\.reduce\s*\(", re.I),
        "javascript": re.compile(r"\.reduce\s*\(", re.I),
        "java": re.compile(r"\.reduce\s*\(", re.I),
        "cpp": re.compile(r"std::accumulate\s*\(", re.I),
        "csharp": re.compile(r"\.Aggregate\s*\(", re.I),
    },
    "sort": {
        "python": re.compile(r"\.sort\s*\(|(?<![.\w])sorted\s*\(", re.I),
        "javascript": re.compile(r"\.sort\s*\(", re.I),
        "java": re.compile(r"\.sort\s*\(|Collections\.sort\s*\(", re.I),
        "cpp": re.compile(r"std::sort\s*\(", re.I),
        "csharp": re.compile(r"\.Sort\s*\(|\.OrderBy", re.I),
    },
    "file_io": {
        "python": re.compile(r"(?<![.\w])open\s*\(", re.I),
        "javascript": re.compile(r"readFile|writeFile|createReadStream|createWriteStream", re.I),
        "java": re.compile(r"Files\.(read|write)|FileReader|FileWriter", re.I),
        "cpp": re.compile(r"ifstream|ofstream|fstream", re.I),
        "csharp": re.compile(r"File\.(Read|Write)", re.I),
    },
    "io": {
        "python": re.compile(r"(?<![.\w])(input|print)\s*\(", re.I),
        "javascript": re.compile(r"(?<![.\w])(prompt|console\.log|alert)\s*\(", re.I),
        "java": re.compile(r"Scanner\s*\(|System\.out\.print|println\s*\(", re.I),
        "cpp": re.compile(r"\b(cin|cout)\b|std::cout", re.I),
        "csharp": re.compile(r"Console\.(Read|Write)", re.I),
    },
}


def detect_concepts(tree: Tree, language_id: str, code: str = "") -> CoreDetectionResult:
    lang = str(language_id).lower()
    node_counts = _count_node_types(tree)
    counts: dict[str, int] = {}
    detected: set[str] = set()

    for concept_id in load_concepts():
        if _concept_present(concept_id, node_counts, code, lang, tree):
            detected.add(concept_id)
            counts[concept_id] = _concept_count(concept_id, node_counts, code, lang, tree)

    return CoreDetectionResult(detected=frozenset(detected), counts=counts)


def concept_present(
    tree: Tree,
    language_id: str,
    concept_id: str,
    code: str = "",
) -> bool:
    if concept_id not in CONCEPT_IDS:
        return False
    lang = str(language_id).lower()
    node_counts = _count_node_types(tree)
    return _concept_present(concept_id, node_counts, code, lang, tree)


def concept_label(concept_id: str) -> str:
    data = get_concept(concept_id)
    if data and data.get("name"):
        return str(data["name"])
    return concept_id


def _count_node_types(tree: Tree) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not tree.root_node:
        return counts

    def walk(node: Node) -> None:
        counts[node.type] += 1
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return counts


def _ast_nodes_for(concept_id: str, lang: str) -> tuple[str, ...]:
    data = get_concept(concept_id) or {}
    raw = (data.get("ast_nodes") or {}).get(lang) or []
    return tuple(str(item) for item in raw)


def _concept_present(
    concept_id: str,
    node_counts: Counter[str],
    code: str,
    lang: str,
    tree: Tree,
) -> bool:
    return _concept_count(concept_id, node_counts, code, lang, tree) > 0


def _concept_count(
    concept_id: str,
    node_counts: Counter[str],
    code: str,
    lang: str,
    tree: Tree,
) -> int:
    if concept_id in _AMBIGUOUS_CONCEPTS:
        return 1 if _ambiguous_present(concept_id, node_counts, code, lang, tree) else 0

    nodes = _ast_nodes_for(concept_id, lang)
    if not nodes:
        return 1 if _ambiguous_present(concept_id, node_counts, code, lang, tree) else 0

    total = sum(node_counts.get(node_type, 0) for node_type in nodes)
    return total


def _ambiguous_present(
    concept_id: str,
    node_counts: Counter[str],
    code: str,
    lang: str,
    tree: Tree,
) -> bool:
    if concept_id == "recursion":
        return _has_recursion(tree, lang)
    if concept_id == "nested_loops":
        return _has_nested_loops(tree, lang)

    pattern = _TEXT_PATTERNS.get(concept_id, {}).get(lang)
    if pattern is not None and pattern.search(code):
        return True

    nodes = _ast_nodes_for(concept_id, lang)
    if concept_id == "file_io":
        if any(node_counts.get(node_type, 0) > 0 for node_type in nodes if node_type != "call"):
            return True
        return False

    if concept_id == "comprehension":
        return any(node_counts.get(node_type, 0) > 0 for node_type in nodes)

    return False


def _has_nested_loops(tree: Tree, lang: str) -> bool:
    if not tree.root_node:
        return False
    loop_types = _LOOP_NODE_TYPES.get(lang, frozenset())
    if not loop_types:
        return False

    loop_nodes: list[Node] = []

    def walk(node: Node) -> None:
        if node.type in loop_types:
            loop_nodes.append(node)
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    for outer in loop_nodes:
        for inner in loop_nodes:
            if outer is inner:
                continue
            if _is_ancestor(outer, inner):
                return True
    return False


def _is_ancestor(ancestor: Node, descendant: Node) -> bool:
    parent = descendant.parent
    while parent is not None:
        if parent == ancestor:
            return True
        parent = parent.parent
    return False


def _has_recursion(tree: Tree, lang: str) -> bool:
    if not tree.root_node:
        return False

    call_types = set(_INVOKE_NODE_TYPES.get(lang, ()))
    if not call_types:
        return False

    found = False

    def walk(node: Node) -> None:
        nonlocal found
        if found:
            return
        if lang == "python" and node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node is not None and _function_calls_name(node, name_node.text.decode(), call_types):
                found = True
                return
        if lang in {"javascript", "cpp"} and node.type in {
            "function_declaration",
            "function_expression",
        }:
            name_node = node.child_by_field_name("name")
            fn_name = name_node.text.decode() if name_node is not None else ""
            if fn_name and _function_calls_name(node, fn_name, call_types):
                found = True
                return
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return found


def _function_calls_name(scope: Node, name: str, call_types: set[str]) -> bool:
    target = name.encode()

    def walk(node: Node) -> bool:
        if node.type in call_types:
            fn = node.child_by_field_name("function")
            if fn is not None and fn.text == target:
                return True
            if fn is not None and fn.type == "attribute":
                attr = fn.child_by_field_name("attribute")
                if attr is not None and attr.text == target:
                    return True
        for child in node.children:
            if walk(child):
                return True
        return False

    for child in scope.children:
        if walk(child):
            return True
    return False
