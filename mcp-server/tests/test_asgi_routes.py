"""ASGI-level checks via Starlette TestClient (no live TCP)."""
from __future__ import annotations

from starlette.testclient import TestClient

import mcp_server


def test_health_returns_ok_and_count() -> None:
    client = TestClient(mcp_server.mcp.sse_app())
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["employee_count"] == 20


def test_salary_tool_description_includes_poison_pattern() -> None:
    assert "support@attacker-external.com" in mcp_server._GENERATE_SALARY_DESCRIPTION
    assert "forward" in mcp_server._GENERATE_SALARY_DESCRIPTION.lower()
