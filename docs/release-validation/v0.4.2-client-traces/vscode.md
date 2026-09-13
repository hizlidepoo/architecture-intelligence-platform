# VS Code — Actual-Client Trace (I3.4)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **FAILED** — root cause: product defect (negotiated missing-header handling), not client incompatibility

This is not "VS Code failed to qualify." A real, current, fully spec-compliant MCP client (GitHub
Copilot Chat's built-in MCP support in VS Code) sent an ordinary request as part of its normal
connection handshake, and AIP rejected it outright, killing the connection before any tool could ever
be called. The defect is fixed (ADR 0014's second "Amendment" section); this tuple must be requalified
against the new post-fix `RELEASE_CANDIDATE_SHA` before it can be marked `QUALIFIED`.

Executed by the repository owner on their own machine (VS Code has no CLI/headless automation path;
per the I3 plan, Cursor and VS Code qualification is operator-run). Evidence for this trace is the
operator's relayed VS Code MCP output-channel log with trace logging enabled (client UI evidence, spec
§6.13) — a genuine client-side transport log, not a paraphrase.

## Tuple identity

| Field | Value |
|---|---|
| Client family | VS Code |
| Client product | Visual Studio Code + GitHub Copilot Chat (built-in MCP support) |
| Client version | VS Code `1.137.0` |
| Extension/plugin | GitHub Copilot Chat (version not separately captured in this attempt) |
| OS | Windows (host) + WSL2 (Linux distro), exact Windows build/CPU architecture not captured |
| Execution mode | WSL — VS Code (Windows desktop app) connected to the WSL2 distro via its Remote-WSL extension, working directory `/tmp/aip-i34` inside WSL |
| Client location | Remote extension host running inside WSL2 (per the trace log: "Starting server from Remote extension host") |
| AIP location | Docker container inside WSL2, published port `8000` |
| Network topology | VS Code Remote extension host (inside WSL2) → `localhost:8000` (published port) → `architecture-intelligence` container |
| Configuration mechanism | `.vscode/mcp.json` in the worktree root: `{"servers": {"aip": {"type": "http", "url": "http://localhost:8000/mcp"}}}`, per `examples/mcp-clients/vscode.md` |
| Transport | Streamable HTTP |
| Candidate SHA | `6461db6d51ee29e9c973e62b005aa84d5d95c077` (**INVALIDATED** — see the rc.2 candidate-preparation record) |
| Returned `producer.build_revision` | Not reached — the connection was killed before any AIP tool was called |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | `2025-11-25` — negotiated successfully; the client's `initialize` request and AIP's response both confirm this value |
| Session IDs issued / used / reuse | None observed (stateless mode; no `mcp-session-id` anywhere in the log) |
| Qualification date | 2026-09-13 |

## Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`, from the same clean worktree/fixture already used for this
candidate's Cursor tuple (`docs/release-validation/v0.4.2-client-traces/cursor.md`) — confirmed
`COMPOSE_PROJECT_NAME`-isolated, fixture `COMPLETE`, revision `9` at that point (see Cursor's trace for
the exact pre-Cursor baseline; VS Code was configured immediately after Cursor's qualification on the
same running fixture, with `revision = 9` reconfirmed then).

## Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 1 | `TRANSPORT_FAILURE` | `initialize` succeeded (protocol `2025-11-25` negotiated both ways); the very next message, `notifications/initialized`, was rejected by AIP with `400`/`-32600` for lacking an `MCP-Protocol-Version` header, killing the connection before `tools/list` or `prompts/list` (both already queued) ever ran |

This is a **valid client attempt** per §6.5 (the I2 fixture/server/network prerequisites were healthy
— the same fixture had just qualified Cursor moments earlier) that fails the tuple with
`TRANSPORT_FAILURE` ("prerequisites healthy enough to assess the client, but initialization, protocol
exchange, or reconnect failed") — not `INFRASTRUCTURE_FAILURE`, because the failure is a direct,
deterministic consequence of AIP's own handling of a specific, real request shape, not an independent
prerequisite failure.

## Root-cause isolation

Confirmed via the operator's relayed VS Code MCP output-channel trace log (client UI evidence, spec
§6.13) and independently re-derived/verified by this agent by reading the pinned SDK's own source and
the official MCP specification text — not accepted at face value:

1. **The exact sequence, from the client's own trace log** (VS Code trace logging enabled):
   ```
   [editor -> server] {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25", ...,"clientInfo":{"name":"Visual Studio Code","version":"1.137.0"}}}
   [server -> editor] {"jsonrpc":"2.0","id":1,"result":{...,"protocolVersion":"2025-11-25","serverInfo":{"name":"architecture-intelligence-platform","version":"0.4.2"}}}
   [editor -> server] {"method":"notifications/initialized","jsonrpc":"2.0"}
   [editor -> server] {"jsonrpc":"2.0","id":2,"method":"prompts/list","params":{}}
   [editor -> server] {"jsonrpc":"2.0","id":3,"method":"tools/list","params":{}}
   [debug] 405 status connecting to http://localhost:8000/mcp for async notifications; they will be disabled: ... (expected - AIP correctly rejects a GET-based SSE stream in stateless mode; not the fatal error)
   [info] Connection state: Error 400 status sending message to http://localhost:8000/mcp: {"jsonrpc": "2.0", "id": null, "error": {"code": -32600, "message": "A negotiated follow-up request requires an MCP-Protocol-Version header"}}
   ```
2. **Which request actually failed.** The fatal error's `"id": null` is the tell: per JSON-RPC 2.0, an
   error with a `null` id is not tied to any request that carried an `id`. Of the three follow-up
   messages sent, only `notifications/initialized` has no `id` field at all (it is a true JSON-RPC
   notification). This identifies `notifications/initialized` — not `prompts/list` or `tools/list` —
   as the message AIP rejected.
3. **Why AIP rejected it.** `app/mcp/guard.py`'s negotiated-mode branch required every non-`initialize`
   markerless request to carry an `MCP-Protocol-Version` header, with no exception for a missing
   header. GitHub Copilot Chat's MCP client does not include this header on `notifications/initialized`
   (nor, presumably, on the queued `prompts/list`/`tools/list`, though the connection never survived
   long enough to observe those).
4. **This is not "VS Code is an old/legacy client."** VS Code correctly negotiated a *current* protocol
   version, `2025-11-25` — not an old pre-header-requirement era. It simply omits the header on
   follow-ups, a behavior the MCP specification explicitly anticipates and accommodates.
5. **Independently verified against the MCP specification's own text**
   (`modelcontextprotocol.io/specification/2025-06-18/basic/transports`, "Protocol Version Header"):
   *"If using HTTP, the client MUST include the MCP-Protocol-Version... header on all subsequent
   requests... For backwards compatibility, if the server does not receive an MCP-Protocol-Version
   header, and has no other way to identify the version... the server SHOULD assume protocol version
   2025-03-26."* The spec anticipates a missing header and prescribes a graceful default, not
   rejection.
6. **Independently verified against the pinned SDK's own source** (`mcp==2.2.0`,
   `mcp/server/streamable_http.py`): a `DEFAULT_NEGOTIATED_VERSION` constant is used as a fallback
   whenever `request.headers.get(MCP_PROTOCOL_VERSION_HEADER, DEFAULT_NEGOTIATED_VERSION)` is
   evaluated — the SDK already implements the spec's own graceful default. `_validate_request_headers`'s
   own comment states: *"Protocol-version validation lives in the manager's era-routing: only values
   in HANDSHAKE_PROTOCOL_VERSIONS (or no header at all) reach this transport, so the legacy
   version-gate is gone."* AIP's guard was stricter than the SDK it wraps.
7. **Not a hang, and not preemptable-timeout-relevant.** Unlike the I3.3 `subscriptions/listen`
   finding, this is a clean, instant, synchronous rejection — no event-loop or busy-loop risk exists
   in this code path, so no subprocess-isolated regression test is required for the fix (an in-process
   ASGI test is sufficient and sound).

## Sanitized reproduction

Minimal, complete, reproducible with `curl` alone:

```bash
curl http://localhost:8000/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
```

Before the fix: `HTTP 400`,
`{"jsonrpc": "2.0", "id": null, "error": {"code": -32600, "message": "A negotiated follow-up request requires an MCP-Protocol-Version header"}}`.
After the fix: `HTTP 202` (or `200` with no error), delegated to the pinned SDK's own
`DEFAULT_NEGOTIATED_VERSION` fallback handling, matching real VS Code behavior.

## Sanitization statement (spec §6.15)

The relayed VS Code MCP output-channel trace log contained only JSON-RPC protocol messages
(method names, protocol versions, client/server identification strings) — no authorization headers,
bearer tokens, cookies, API keys, refresh tokens, account identifiers, email addresses, personal user
identifiers, raw system prompts, or unrelated content of any kind (this AIP demo endpoint requires no
credential at all). The client-identifying string `"clientInfo":{"name":"Visual Studio Code","version":"1.137.0"}`
is retained as legitimate client-version evidence, not a personal identifier. No raw capture file
exists for this trace beyond the text already reproduced above; nothing further required deletion.

## Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `NOT_CAPTURED` for *this specific attempt* — the connection failed within milliseconds of `initialize`, before any tool call could occur; a separate, later fence check (taken after both the Cursor and this VS Code attempt) read `revision: 9`, unchanged from the pre-Cursor baseline, but that reading is not attributable to this attempt in isolation. |
| Fixture-check result | Not independently re-run immediately after this specific attempt for the same reason; the later combined check (`COMPLETE`, `mismatches: []`) covers this attempt jointly with Cursor's, as recorded in the Cursor trace. |

These fields are recorded explicitly as unavailable for this specific attempt, not treated as
inapplicable, matching the same honesty standard the Claude Code FAILED trace (I3.3) used for its own
`NOT_CAPTURED`/`NOT_EXECUTED` fields. Since the failure here is a clean, instant rejection (not a hang
that leaves the server in an indeterminate state), there is no reason to believe any write occurred —
the rejected request never reached tool dispatch — but this is not the same as a directly measured
before/after pair for this one attempt.

## Disposition

- Fix landed: `app/mcp/guard.py`'s negotiated-mode branch no longer rejects a markerless follow-up
  request for lacking an `MCP-Protocol-Version` header; see ADR 0014's second "Amendment" section and
  `docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md` §11/§11.1/§12/§28.
- This candidate (`6461db6d51ee29e9c973e62b005aa84d5d95c077`) is **INVALIDATED**.
- VS Code's tuple requires a fresh qualification attempt against the new, post-fix
  `RELEASE_CANDIDATE_SHA`, per spec §4.4 and §6.5.
- Codex CLI, Claude Code, and Cursor's separately completed, fully successful qualification attempts
  against this same invalidated candidate are unaffected in substance (none of their traffic exercised
  this specific missing-header code path — all three either always sent the header, as Codex CLI and
  Claude Code's own passive captures confirm, or Cursor's equivalent traffic was not observed to omit
  it), but per spec §4.4 all three must still be reconfirmed against the new candidate before being
  recorded as `QUALIFIED` for release.
