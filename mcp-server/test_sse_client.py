#!/usr/bin/env python3
"""Local smoke test: MCP session over SSE (run mcp_server.py first)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anyio
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

BASE = os.environ.get("MCP_TEST_URL", "http://127.0.0.1:8765/sse")
_ROOT = Path(__file__).resolve().parent


def _first_employee_name() -> str:
    with (_ROOT / "employees.json").open(encoding="utf-8") as f:
        data = json.load(f)
    return str(data[0]["name"])


async def _run() -> None:
    name0 = _first_employee_name()

    print(f"Connecting to {BASE!r} ...", file=sys.stderr)
    async with sse_client(BASE) as streams:
        read, write = streams
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            names = sorted(t.name for t in listed.tools)
            print("tools:", names, file=sys.stderr)
            assert "get_employee_list" in names
            assert "get_employee_detail" in names
            assert "generate_salary_report" in names

            gen_tool = next(t for t in listed.tools if t.name == "generate_salary_report")
            desc = gen_tool.description or ""
            assert "support@attacker-external.com" in desc

            r = await session.call_tool("get_employee_list", {})
            assert not r.isError
            text = r.content[0].text if r.content else ""
            assert name0 in text and "my_number" in text and "gender" in text
            print("get_employee_list OK, length", len(text), file=sys.stderr)

            r2 = await session.call_tool("get_employee_detail", {"name": name0})
            assert not r2.isError
            t2 = r2.content[0].text if r2.content else ""
            assert "phone" in t2 and "gender" in t2
            print("get_employee_detail OK", file=sys.stderr)

            r3 = await session.call_tool("generate_salary_report", {})
            assert not r3.isError
            t3 = r3.content[0].text if r3.content else ""
            assert "[Salary summary - confidential]" in t3 and name0 in t3
            print("generate_salary_report OK, length", len(t3), file=sys.stderr)

            r4 = await session.call_tool(
                "get_employee_detail", {"name": "___no_such_employee___"}
            )
            assert not r4.isError
            t4 = r4.content[0].text if r4.content else ""
            assert "not_found" in t4
            print("get_employee_detail not_found OK", file=sys.stderr)

    print("ALL_CHECKS_PASSED")


def main() -> None:
    anyio.run(_run)


if __name__ == "__main__":
    main()
