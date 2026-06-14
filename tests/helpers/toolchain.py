from __future__ import annotations

import shutil

import pytest


def require_fpc() -> None:
    if shutil.which("fpc") is None:
        pytest.fail(
            "fpc (Free Pascal Compiler) должен быть установлен. "
            "macOS: brew install fpc; Debian/Ubuntu: apt install fp-compiler"
        )
