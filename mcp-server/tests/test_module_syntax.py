"""Sanity: server module compiles."""
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_mcp_server_py_compiles() -> None:
    py_compile.compile(str(ROOT / "mcp_server.py"), doraise=True)
