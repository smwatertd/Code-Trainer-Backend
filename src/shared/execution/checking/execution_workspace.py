from __future__ import annotations

import uuid


def new_workspace_id() -> str:
    return uuid.uuid4().hex[:16]


def workspace_root(workspace_id: str) -> str:
    safe = "".join(character for character in workspace_id if character.isalnum())
    if not safe:
        safe = uuid.uuid4().hex[:16]
    return f"/tmp/home/{safe}"


def source_path(workspace_id: str, ext: str) -> str:
    normalized_ext = ext if ext.startswith(".") else f".{ext}"
    return f"{workspace_root(workspace_id)}/source{normalized_ext}"


def binary_path(workspace_id: str) -> str:
    return f"{workspace_root(workspace_id)}/app"


def isolation_shell_prefix(workspace_id: str) -> str:
    root = workspace_root(workspace_id)
    return f'CT_WORKSPACE="{root}"; ' f'mkdir -p "$CT_WORKSPACE" && ' f"trap 'rm -rf \"$CT_WORKSPACE\"' EXIT INT TERM; "
