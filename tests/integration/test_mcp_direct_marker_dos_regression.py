"""v0.4.2 I1 amendment (PR #145 review) - the exact real-world `subscriptions/listen` reproduction
that found the single-request DoS `app/mcp/guard.py`'s `_DIRECT_MODE_METHODS` allowlist fixes.

This is deliberately NOT an in-process `httpx.ASGITransport` test wrapped in `asyncio.wait_for`
(that was the first version of this test, in `tests/unit/test_mcp_discovery.py`): this defect's own
root cause is that the offending SDK code never yields control back to the event loop once it starts,
so `asyncio.wait_for` cannot preempt it - confirmed by git-stash-verifying that the in-process version
hung the *entire* pytest process indefinitely without the fix, not just one test.

Runs the guard-wrapped app in a genuinely separate OS process (real `uvicorn`, real loopback TCP, the
same server this project's `Dockerfile` runs) so a regression is bounded by an ordinary client-side
socket timeout - enforced by the OS, not by anything inside the (possibly hung) child's own event
loop - and, on top of that, an explicit parent-side `subprocess`/socket timeout that always terminates
the child, so a regression here fails this test promptly instead of hanging the CI job until its own
outer timeout.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from .support.live_server import free_loopback_port

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_STARTUP_TIMEOUT_SECONDS = 15.0
_REQUEST_TIMEOUT_SECONDS = 5.0

_CHILD_SERVER_SCRIPT = textwrap.dedent(
    """
    import sys

    import uvicorn

    from app.mcp.app import build_mcp_app
    from app.mcp.tools import register_tools
    from mcp.server import MCPServer

    # No manual `mcp_session_manager_lifespan(server)` wrap here: unlike the in-process
    # ASGITransport unit tests (which never receive real ASGI lifespan events and so must enter it
    # explicitly), a real uvicorn server sends a genuine `lifespan.startup` event straight through
    # `ModernProtocolGuard` to the SDK's own mounted app, which owns `session_manager.run()` as
    # *its* lifespan - matching exactly how `app.main`'s real production FastAPI app wires it
    # (`stack.enter_async_context(mcp_session_manager_lifespan())` inside FastAPI's own lifespan,
    # triggered once by uvicorn, never a second explicit entry).
    port = int(sys.argv[1])
    server = MCPServer(name="dos-regression-test", version="0.4.2")
    register_tools(server)
    app = build_mcp_app(
        allowed_origins=[f"http://127.0.0.1:{port}"],
        allowed_hosts=[f"127.0.0.1:{port}"],
        server=server,
    )

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
    """
)


def _wait_for_port(port: int, *, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/mcp", timeout=1):
                return
        except urllib.error.HTTPError:
            return  # any HTTP response (even an error) proves the server is up
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.05)
    raise TimeoutError(f"child server did not start listening on port {port} within {timeout}s")


def test_subscriptions_listen_cannot_hang_the_server() -> None:
    """The exact real Claude Code repro. Regressing the fix must fail this test within a few
    seconds, never hang the suite or the CI job."""
    port = free_loopback_port()
    proc = subprocess.Popen(
        [sys.executable, "-c", _CHILD_SERVER_SCRIPT, str(port)],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        try:
            _wait_for_port(port, timeout=_STARTUP_TIMEOUT_SECONDS)
        except TimeoutError:
            proc.terminate()
            output = proc.communicate(timeout=5)[0]
            pytest.fail(f"child server never started listening:\n{output}")

        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "listen:0",
                "method": "subscriptions/listen",
                "params": {
                    "_meta": {
                        "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                        "io.modelcontextprotocol/clientCapabilities": {},
                    },
                    "notifications": {"toolsListChanged": True},
                },
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/mcp",
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "accept": "application/json, text/event-stream",
                "origin": f"http://127.0.0.1:{port}",
                "mcp-method": "subscriptions/listen",
                "mcp-protocol-version": "2026-07-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
                status = response.status
                payload = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            status = exc.code
            payload = json.loads(exc.read())
        except (TimeoutError, urllib.error.URLError) as exc:
            pytest.fail(
                f"subscriptions/listen did not respond within {_REQUEST_TIMEOUT_SECONDS}s "
                f"({exc!r}) - the single-request DoS this allowlist is supposed to prevent has "
                "regressed"
            )

        assert status == 404
        error = payload["error"]
        assert error["code"] == -32601
        assert error["data"] == "subscriptions/listen"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
