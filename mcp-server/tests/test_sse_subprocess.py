"""Full MCP over HTTP+SSE: spawn server on ephemeral port, run client script."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _pick_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_http_ok(url: str, timeout_s: float = 15.0) -> None:
    deadline = time.monotonic() + timeout_s
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as r:
                if r.status == 200:
                    return
        except (urllib.error.URLError, OSError) as e:
            last = e
        time.sleep(0.15)
    raise AssertionError(f"server did not become ready: {url}, last error: {last}")


def test_mcp_sse_end_to_end_subprocess() -> None:
    port = _pick_free_port()
    env = os.environ.copy()
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_PORT"] = str(port)
    env["LOG_LEVEL"] = "WARNING"

    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "mcp_server.py")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_http_ok(f"http://127.0.0.1:{port}/health")

        env2 = env.copy()
        env2["MCP_TEST_URL"] = f"http://127.0.0.1:{port}/sse"
        run = subprocess.run(
            [sys.executable, str(ROOT / "test_sse_client.py")],
            cwd=str(ROOT),
            env=env2,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert run.returncode == 0, f"stdout:\n{run.stdout}\nstderr:\n{run.stderr}"
        assert "ALL_CHECKS_PASSED" in run.stdout
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)