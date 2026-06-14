from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
LANGUAGES_DIR = BACKEND_ROOT / "languages"
RUFF_STUDENT_CONFIG = LANGUAGES_DIR / "ruff-student.toml"
