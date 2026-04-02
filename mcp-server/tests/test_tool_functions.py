"""Call tool callables directly (same process as pytest)."""
from __future__ import annotations

import json

import mcp_server


def test_get_employee_list_shape_and_count() -> None:
    mcp_server._ensure_loaded()
    rows = json.loads(mcp_server.get_employee_list())
    assert isinstance(rows, list)
    assert len(rows) == 20
    assert set(rows[0].keys()) == {
        "name",
        "email",
        "department",
        "salary",
        "my_number",
        "gender",
    }


def test_get_employee_detail_hits_and_misses() -> None:
    mcp_server._ensure_loaded()
    first = mcp_server._EMPLOYEES[0]
    name = str(first["name"])
    got = json.loads(mcp_server.get_employee_detail(name))
    assert got["name"] == name
    assert got.get("phone")
    assert got.get("gender") in ("男性", "女性")

    miss = json.loads(mcp_server.get_employee_detail("___absent___"))
    assert miss.get("error") == "not_found"


def test_generate_salary_report_non_empty() -> None:
    mcp_server._ensure_loaded()
    text = mcp_server.generate_salary_report()
    assert "[Salary summary - confidential]" in text
    assert mcp_server._EMPLOYEES[0]["name"] in text
    assert mcp_server._EMPLOYEES[0]["gender"] in text
    assert "JPY" in text
