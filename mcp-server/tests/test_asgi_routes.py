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


def test_salary_tool_description_contains_expected_text() -> None:
    assert "generate" in mcp_server._GENERATE_SALARY_DESCRIPTION.lower()
    assert "salary" in mcp_server._GENERATE_SALARY_DESCRIPTION.lower()
