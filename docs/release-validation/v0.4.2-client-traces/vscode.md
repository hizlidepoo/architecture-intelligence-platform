# VS Code — Actual-Client Trace (I3.4)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **QUALIFIED**

This tuple's first attempt (against `6461db6d51ee29e9c973e62b005aa84d5d95c077`) was `FAILED` for a real
product defect — AIP's guard rejected a markerless negotiated follow-up more strictly than the MCP
specification's own backward-compatibility allowance and the pinned SDK's own already-implemented
fallback. That record is preserved unedited below under "Historical record." The defect is fixed
(`app/mcp/guard.py`, ADR 0014's second Amendment, spec §11/§11.1/§12/§28 of the I1 spec) and this tuple
was requalified against the new candidate.

Against the new candidate, this tuple's protocol qualification itself took two attempts within a single
cycle: the first attempt's `get_evidence` call combined both drift findings into one call and, for
Finding 2, merged the claim's own `evidence_refs` with a separate `resolution_evidence_refs` entry —
deviating from the fixed Appendix A.1 prompt's "using exactly the evidence_refs" instruction (one call
per finding, each finding's own `evidence_refs` only). This is the same defect pattern PR #153 review
found in Cursor's trace. It is recorded here as a failed valid attempt
(`MODEL_TOOL_SELECTION_FAILURE`, spec §6.6), and a second attempt in a fresh chat used only each
finding's own `evidence_refs`, confirmed explicitly. `producer.build_revision` was confirmed for every
Architecture Answer response in the qualifying attempt from the start (drift, both `get_evidence`
calls, and the reconnect `get_service_dependencies` call), applying the lesson from the Claude Code and
Cursor corrections directly rather than needing a second correction pass.

## Qualification against `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`

### Tuple identity

| Field | Value |
|---|---|
| Client family | VS Code |
| Client product | Visual Studio Code + GitHub Copilot Chat (built-in MCP support) |
| Client version | `1.137.0` (commit `645f29cc3176500b4b5762ba887cf2a7f0ffdf2c`) |
| Extension/plugin | GitHub Copilot Chat — `@github/copilot 1.0.84.70.gdb75d0d` (`@github/copilot-sdk 1.0.13-preview.4`) |
| OS | Windows_NT x64 `10.0.26200` (host), WSL2 (Linux distro) for AIP and the working directory |
| Execution mode | WSL — VS Code (Windows desktop app, Electron `42.10.0`) connected to the WSL2 distro via Remote-WSL, working directory `/tmp/aip-vscode` inside WSL |
| Client location | Remote extension host running inside WSL2 |
| AIP location | Docker container inside WSL2, published port `8000` |
| Network topology | VS Code Remote extension host (inside WSL2) → `localhost:8000` (WSL2 published port) → `architecture-intelligence` container |
| Configuration mechanism | `.vscode/mcp.json` in the worktree root: `{"servers": {"aip": {"type": "http", "url": "http://localhost:8000/mcp"}}}`, per `examples/mcp-clients/vscode.md` |
| Transport | Streamable HTTP |
| Approval mode | Automatic — operator confirmed all tool calls across all three runs (the qualifying attempt, reconnect, UX observation) executed without any approve/allow prompt |
| Candidate SHA | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` |
| Returned `producer.build_revision` | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` — exact match, confirmed for **every** Architecture Answer response in the qualifying attempt (`get_architecture_drift`, both `get_evidence` calls, and the reconnect `get_service_dependencies` call), each asked as a direct follow-up quoting the field from the response already returned |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | Not independently captured for this run (no trace-level JSON-RPC capture was taken this time, unlike the historical FAILED attempt); the MCP output-channel log (info level) confirms `Connection state: Running` and `Discovered 3 tools` for every connect/reconnect cycle |
| Session IDs issued / used / reuse | Not independently captured for the same reason; consistent with every other client family's evidence that AIP's negotiated mode issues none |
| Qualification date | 2026-09-14 |

Configuration re-verification is unchanged from the historical record — `.vscode/mcp.json`'s shape was
reverified against VS Code's official docs source on 2026-09-12 (see `examples/mcp-clients/vscode.md`'s
own verification record) and is not repeated in full here.

### Pre-client state (spec §6.2/§6.3) — captured directly, before any client interaction

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`50862a352626ea38d2fbb36f2ff0ecfc667266d0`, run fresh and dedicated to this VS Code trace alone — unlike
the historical FAILED attempt's shared-with-Cursor baseline, this fixture instance was never touched by
any other client. This agent had direct shell access to the same host running the fixture and ran
`check_fixture_state.py`/`read_revision_fence.py` itself, immediately after `--serve` completed and
*before* `.vscode/mcp.json` was even created: `fixture = COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
`revision_before = 9`.

### Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 1 | `MODEL_TOOL_SELECTION_FAILURE` | Fixed Appendix A.1 prompt pasted verbatim, fresh chat. Called `get_architecture_drift` correctly, but issued a single `get_evidence` call combining both findings' `evidence_refs` **and**, for Finding 2, the separate `resolution_evidence_refs` entry `evidence:otel:demo:2026-08-26:29d4976aeaf9` — deviating from the fixed prompt's "for every returned finding, call get_evidence using exactly the evidence_refs" instruction (one call per finding, each finding's own `evidence_refs` only). Prerequisites were healthy and the model otherwise executed correctly, so this is a valid attempt that failed on model tool selection, not infrastructure or client control. |
| 2 | — | Fresh chat, same fixed Appendix A.1 prompt pasted verbatim. Called `get_architecture_drift`, then issued two separate `get_evidence` calls, each using only that finding's own `evidence_refs` (Finding 1: `["evidence:asyncapi:order-service"]`; Finding 2: `["evidence:otel:demo:2026-08-26:bfae54276215"]`, no `resolution_evidence_refs`). `producer.build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` confirmed via direct follow-up for the drift call and both `get_evidence` calls. |

Per §6.6, one `MODEL_TOOL_SELECTION_FAILURE` on the LLM-mediated path permits exactly one further valid
attempt, which attempt 2 is. Two valid client attempts total, within the per-cycle budget of 2 (spec
§6.5); no infrastructure-invalidated runs occurred.

### Required successful protocol workflow (spec §6.8)

This table describes attempt 2 (the qualifying attempt) and its own reconnect. Evidence source is the
operator's relayed chat transcripts and the VS Code MCP output-channel log lines (client UI evidence,
spec §6.13); the pre-/post-client fixture and revision checks were run directly by this agent (see
above and below), not relayed.

| # | Requirement | Evidence |
|---|---|---|
| 1 | Initialization/negotiation | MCP output-channel log: `Starting server aip` → `Connection state: Running` (2026-09-14 09:55:08). |
| 2 | Tool discovery | Same log, immediately after: `Discovered 3 tools` (09:55:09). |
| 3 | Exactly three AIP tools discovered | `get_architecture_drift`, `get_evidence`, `get_service_dependencies` — matching the tool calls made across the session and the log's own tool count. |
| 4 | `get_architecture_drift` | Drift called for `service:order-service`, `demo`, `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`. `producer.build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` confirmed via direct follow-up. |
| 5 | Deterministic structured drift result | `queue:unused-q` → `NOT_OBSERVED_IN_WINDOW` (coverage `SUFFICIENT`, `UNRESOLVED_IDENTITY` limitation) and `service:legacypricingservice` (via `GET /pricing/{sku}`) → `OBSERVED_ONLY` — the exact spec §6.9 expected result. |
| 6 | `get_evidence` using exactly the returned `evidence_refs` | Finding 1: `evidence_refs: ["evidence:asyncapi:order-service"]`. Finding 2: `evidence_refs: ["evidence:otel:demo:2026-08-26:bfae54276215"]` — the claim's own `evidence_refs` only, no `resolution_evidence_refs`. Both `producer.build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` confirmed via direct follow-up. |
| 7 | Same snapshot used | All calls (drift, both `get_evidence`) carry `snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | Operator stopped the `aip` server via MCP: List Servers. Log: `Stopping server aip` → `Connection state: Stopped` (10:04:55). |
| 9 | Reconnect/reinitialize | Operator started `aip` again via the same command. Log: `Starting server aip` → `Connection state: Running` → `Discovered 3 tools` (10:05:14). A fresh chat then successfully called AIP's tools again from scratch. |
| 10 | One read-only tool works after reconnect | `get_service_dependencies` for `service:order-service` returned `outcome: PARTIAL` with 3 dependency claims (`product-service`, `payment-service`, `unused-q`, all `NOT_OBSERVED_IN_WINDOW`), same pinned `snapshot_id`; `producer.build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` confirmed via direct follow-up. Copilot Chat defaulted the observation window to "today" (`2026-09-14`) rather than reusing the demo window, since it was not told one for this call — spec §6.11 requires only tool discovery plus one successful read-only call for reconnect (the same window and the §6.9 deterministic result are required only for the qualifying attempt itself, not the reconnect check), which this satisfies. |

### Sanitization statement (spec §6.15)

All evidence in this section is text and MCP output-channel log lines relayed directly by the
repository owner, describing only AIP architecture-fact content and JSON-RPC connection-state/tool-
count lines — no authorization headers, tokens, cookies, account identifiers, email addresses, personal
identifiers, raw system prompts, or unrelated content of any kind. AIP's local demo endpoint requires no
credential.

### Post-client state (spec §6.12/§6.15) — captured directly, after the entire tuple including the UX run

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`), measured directly by this agent via `read_revision_fence.py --json`, run *after* attempt 2's drift/`get_evidence` calls, the reconnect/`get_service_dependencies` call, **and** the separate Appendix A.2 UX run below — all on one continuous fixture instance dedicated to this trace alone. |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged, matching every snapshot ID quoted throughout the run. |

Unlike Cursor's tuple, this trace's entire session — the failed attempt 1, the qualifying attempt 2, the
reconnect, and the UX run — ran on one continuous fixture instance with no teardown in between, so this
is a genuine single tuple-local `R' = R` proof covering the whole session end to end.

### Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh Copilot Chat, after protocol qualification (attempt 2) and its reconnect had already
completed.

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Where visible:**

| | |
|---|---|
| Model/provider | Claude Sonnet 4.6 |
| Agent mode | GitHub Copilot Chat's Agent mode |
| Tool approval mode | Automatic — no approval prompt requested or reached |

**§7.2 result table** (`YES` / `NO` / `PARTIAL` / `NOT_OBSERVED`):

| Observation | Result |
|---|---|
| selected AIP | `YES` |
| called `get_architecture_drift` | `YES` |
| found `LegacyPricingService` | `YES` |
| preserved `OBSERVED_ONLY` | `YES` |
| found `unused-q` | `YES` |
| preserved `NOT_OBSERVED_IN_WINDOW` | `YES` |
| called `get_evidence` | `YES` |
| preserved the same snapshot | `YES` |
| distinguished evidence from inference | `YES` |
| avoided unused/dead/obsolete overclaim | `YES` |

**Unedited observed outcome** (the agent's response, as relayed verbatim by the operator — sanitization
statement above):

> Here are the two drift findings, fully resolved against the same snapshot
> (`aip:snapshot:v1:685a341…`).
>
> **Finding 1 — `NOT_OBSERVED_IN_WINDOW`**
> Claim: `aip:claim:v1:ca0dd73b…`
> Relation: `service:order-service` –[SENDS]→ `queue:unused-q`
> Destination resolution: `DIRECT_TARGET_FALLBACK`
>
> Qualification: `NOT_OBSERVED_IN_WINDOW` with `coverage: SUFFICIENT`. The spec declares this send; no
> OpenTelemetry observation of it appeared in the 2026-08-26 window. Because declared coverage was
> deemed sufficient to judge absence, AIP flags it as drift: a behaviour the architecture says must
> exist was not seen.
>
> Evidence: `evidence:asyncapi:order-service` (`DECLARED / ASYNCAPI`, `asyncapi.yaml`) — declares
> `SENDS service:order-service → queue:unused-q`, `CARRIES queue:unused-q → message:UnusedMessage`,
> `CONFORMS_TO message:UnusedMessage → schema:UnusedMessage`. `resolution_evidence_refs` is empty — no
> observed evidence contributed to destination resolution.
>
> Limitation: `UNRESOLVED_IDENTITY` — "queue:unused-q has no single evidenced consumer service;
> retained as the direct queue target rather than guessed." AIP could not resolve the queue to a
> downstream service because no evidence record establishes a consumer.
>
> What AIP established: the AsyncAPI spec declares order-service sends to queue:unused-q; no OTel trace
> for that send appeared in the 2026-08-26 window; queue:unused-q has no evidenced consumer in this
> snapshot. AIP does not establish why no trace was observed, or whether a consumer exists outside this
> snapshot.
>
> **Finding 2 — `OBSERVED_ONLY`**
> Claim: `aip:claim:v1:8c43c7b5…`
> Relation: `service:order-service` –[CALLS]→ `operation:service:legacypricingservice:GET:/pricing/{sku}` → `service:legacypricingservice`
> Destination resolution: `RESOLVED_SERVICE`
>
> Qualification: `OBSERVED_ONLY`. A call to LegacyPricingService was seen in telemetry but there is no
> corresponding declared evidence. `coverage` is null because there is no declared claim to measure
> against.
>
> Evidence: `evidence:otel:demo:2026-08-26:bfae54276215` (`OBSERVED / OPENTELEMETRY`, `CLIENT_SERVER`,
> window 2026-08-26) declares `CALLS service:order-service → operation:service:legacypricingservice:GET:/pricing/{sku}`,
> first/last seen `2026-08-26T12:00:00.044222Z`, 1 observation. Resolution evidence
> `evidence:otel:demo:2026-08-26:29d4976aeaf9` (same envelope) declares
> `PROVIDES service:legacypricingservice → that same operation` — this is what let AIP resolve the
> operation to `service:legacypricingservice` (`RESOLVED_SERVICE`).
>
> What AIP established: on 2026-08-26 at 12:00 UTC, service:order-service made exactly one
> `GET /pricing/{sku}` call to service:legacypricingservice, corroborated by a matching server-side
> span; this dependency is absent from every declared source in the snapshot. AIP does not establish
> whether the call is intentional, a bug, or recent; nor call volume beyond the single observed
> occurrence, nor whether it recurs outside this window.

This is observational product evidence only, not a semantic release gate (spec §7.2).

### Disposition

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`, on attempt 2
  (see Attempt record) — attempt 1 is `MODEL_TOOL_SELECTION_FAILURE` and superseded.
- The historical `FAILED` result against the invalidated candidate was a real product defect, not a
  client incompatibility to work around; it is fixed and this requalification is against the fix.
- Every pre-/post-client fixture and revision check in this qualification was captured directly by this
  agent on a fixture instance dedicated to this trace alone — a genuine, single, tuple-local `R' = R`
  proof covering the entire session end to end (qualifying attempt, reconnect, and UX run).
- `producer.build_revision` is confirmed for every Architecture Answer response in the qualifying
  attempt (drift, both `get_evidence` calls, and the reconnect call), applied from the start rather than
  needing a later correction.

## Historical record: `FAILED` attempt against invalidated candidate `6461db6d51ee29e9c973e62b005aa84d5d95c077`

### Root cause: product defect (AIP was stricter than the spec's own backward-compatibility allowance), not merely client incompatibility

This is not simply "VS Code failed to qualify," but it is also not "VS Code did nothing wrong." Two
distinct normative statements are both true at once, per the MCP specification's own Protocol Version
Header section (`basic/transports#protocol-version-header`):

- The client **MUST** include `MCP-Protocol-Version` on every subsequent HTTP request. GitHub Copilot
  Chat's built-in MCP client in VS Code was directly observed omitting this header on
  `notifications/initialized` — that omission is itself **not** spec-conformant client behavior. (Its
  queued `prompts/list`/`tools/list` calls never completed once the connection died on that
  notification, so whether they too would have omitted the header was never observed — the fix covers
  every markerless follow-up as a general contract requirement, not a claim that those two calls were
  confirmed headerless as well.)
- Separately, for backward compatibility, a server that receives no such header and has no other way
  to identify the version **SHOULD assume** protocol version `2025-03-26` rather than reject the
  request outright.

AIP's guard implemented neither of these correctly: it enforced the client-side `MUST` as a hard
rejection at the transport layer, with no allowance for the server-side `SHOULD` tolerate this exact
case. The practical effect was a real, widely-used client (VS Code 1.137.0 + GitHub Copilot Chat)
being unable to connect to AIP at all, in any invocation — a release-blocking interoperability defect,
independent of whose spec obligation was actually violated. The defect is fixed (ADR 0014's second
"Amendment" section) to make AIP tolerant per the spec's own backward-compatibility clause; this tuple
must be requalified against the new post-fix `RELEASE_CANDIDATE_SHA` before it can be marked
`QUALIFIED`.

Executed by the repository owner on their own machine (VS Code has no CLI/headless automation path;
per the I3 plan, Cursor and VS Code qualification is operator-run). Evidence for this trace is the
operator's relayed VS Code MCP output-channel log with trace logging enabled (client UI evidence, spec
§6.13) — a genuine client-side transport log, not a paraphrase.

### Tuple identity

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

### Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`, run once and shared across this candidate's Cursor and VS
Code tuples — this was **not** a fresh `--serve` dedicated to VS Code alone, and this is stated
plainly rather than implying otherwise.

`check_fixture_state.py`/`read_revision_fence.py` were run exactly once during this shared session:
after Cursor's three chat interactions had already completed, and *before* VS Code was configured or
touched AIP in any way (`fixture = COMPLETE`, `mismatches: []`, `revision = 9`; see that same reading
recorded as Cursor's *post*-client state in `docs/release-validation/v0.4.2-client-traces/cursor.md`,
which is `UNVERIFIED` precisely because no baseline exists *before* Cursor — this reading does not
establish one for Cursor, and this trace does not claim otherwise). Chronologically, that single
reading sits strictly between Cursor's interactions and VS Code's, so it legitimately serves as this
tuple's own `revision_before = 9`/`fixture = COMPLETE` pre-client baseline — no VS Code traffic had
occurred yet — but it is a baseline for a fixture that Cursor's three (read-only) tool calls had
already exercised, not a pristine post-seed state. This distinction matters if this trace is ever read
as evidence for anything about the fixture's state before *any* client touched it; it is not that, and
is not offered as that.

### Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 1 | `TRANSPORT_FAILURE` | `initialize` succeeded (protocol `2025-11-25` negotiated both ways); the very next message, `notifications/initialized`, was rejected by AIP with `400`/`-32600` for lacking an `MCP-Protocol-Version` header, killing the connection before `tools/list` or `prompts/list` (both already queued) ever ran |

This is a **valid client attempt** per §6.5 (the I2 fixture/server/network prerequisites were healthy
— the same fixture had just handled several Cursor interactions moments earlier, with the fixture
checker reporting `COMPLETE`, `mismatches: []` at that point) that fails the tuple with
`TRANSPORT_FAILURE` ("prerequisites healthy enough to assess the client, but initialization, protocol
exchange, or reconnect failed") — not `INFRASTRUCTURE_FAILURE`, because the failure is a direct,
deterministic consequence of AIP's own handling of a specific, real request shape, not an independent
prerequisite failure.

### Root-cause isolation

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
   header. GitHub Copilot Chat's MCP client is directly confirmed, via its own trace log, not to
   include this header on `notifications/initialized`. Its queued `prompts/list`/`tools/list` calls
   never completed once the connection died on that notification, so whether those two calls would
   also have omitted the header was never observed one way or the other — this finding and the fix
   that follows do not depend on that being true, only on the one directly observed case.
4. **This is not "VS Code is an old/legacy client."** VS Code correctly negotiated a *current* protocol
   version, `2025-11-25` — not an old pre-header-requirement era. It omitted the header on the one
   follow-up observed regardless, which is not itself spec-conformant client behavior (see next point)
   — but the spec
   directs servers to tolerate exactly this gracefully rather than reject it.
5. **Independently verified against the MCP specification's own text**
   (`modelcontextprotocol.io/specification/2025-11-25/basic/transports`, "Protocol Version Header"):
   *"If using HTTP, the client MUST include the MCP-Protocol-Version... header on all subsequent
   requests... For backwards compatibility, if the server does not receive an MCP-Protocol-Version
   header, and has no other way to identify the version... the server SHOULD assume protocol version
   2025-03-26."* These are two distinct, both-true normative statements: VS Code's own omission is a
   **client-side non-conformance** (the `MUST` is violated), while AIP's outright rejection was a
   separate, **server-side non-conformance** (the `SHOULD assume ... 2025-03-26` backward-compatibility
   allowance was not honored). Fixing AIP's side does not retroactively make VS Code's traffic
   spec-conformant — it makes AIP correctly tolerant of real-world non-conformant traffic exactly as
   the spec's own backward-compatibility clause directs.
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

### Sanitized reproduction

Minimal, complete, reproducible with `curl` alone:

```bash
curl http://localhost:8000/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
```

Before the fix: `HTTP 400`,
`{"jsonrpc": "2.0", "id": null, "error": {"code": -32600, "message": "A negotiated follow-up request requires an MCP-Protocol-Version header"}}`.
After the fix: `HTTP 202 Accepted`, empty body — the exact contract the transport spec requires for an
accepted notification, matching `_check_vscode_full_sequence_without_protocol_header_is_accepted`'s
own assertion in `tests/unit/test_mcp_discovery.py`, not a looser "202 or 200" expectation. Delegated
to the pinned SDK's own `DEFAULT_NEGOTIATED_VERSION` fallback handling, matching real VS Code
behavior.

### Sanitization statement (spec §6.15)

The relayed VS Code MCP output-channel trace log contained only JSON-RPC protocol messages
(method names, protocol versions, client/server identification strings) — no authorization headers,
bearer tokens, cookies, API keys, refresh tokens, account identifiers, email addresses, personal user
identifiers, raw system prompts, or unrelated content of any kind (this AIP demo endpoint requires no
credential at all). The client-identifying string `"clientInfo":{"name":"Visual Studio Code","version":"1.137.0"}`
is retained as legitimate client-version evidence, not a personal identifier. No raw capture file
exists for this trace beyond the text already reproduced above; nothing further required deletion.

### Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `NOT_CAPTURED` for this attempt — the connection failed within milliseconds of `initialize`, before any tool call could occur, and no fence check was run afterward specifically for this attempt. (The `revision = 9` reading discussed under Pre-client state above was taken *before* this attempt, not after it — it is this tuple's pre-client baseline, not a post-attempt reading, and is not being reused here as one.) |
| Fixture-check result | Likewise `NOT_EXECUTED` for this specific attempt, for the same reason — no re-check was run immediately after the failure. |

These fields are recorded explicitly as unavailable for this specific attempt, not treated as
inapplicable, matching the same honesty standard the Claude Code FAILED trace (I3.3) used for its own
`NOT_CAPTURED`/`NOT_EXECUTED` fields. Since the failure here is a clean, instant rejection (not a hang
that leaves the server in an indeterminate state), there is no reason to believe any write occurred —
the rejected request never reached tool dispatch — but this is not the same as a directly measured
before/after pair for this one attempt.

### Disposition

- Fix landed: `app/mcp/guard.py`'s negotiated-mode branch no longer rejects a markerless follow-up
  request for lacking an `MCP-Protocol-Version` header; see ADR 0014's second "Amendment" section and
  `docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md` §11/§11.1/§12/§28.
- This candidate (`6461db6d51ee29e9c973e62b005aa84d5d95c077`) is **INVALIDATED**.
- VS Code's tuple requires a fresh qualification attempt against the new, post-fix
  `RELEASE_CANDIDATE_SHA`, per spec §4.4 and §6.5.
- None of Codex CLI's, Claude Code's, or Cursor's traffic against this same invalidated candidate is
  known to have exercised this specific missing-header code path. Codex CLI and Claude Code's own
  passive captures directly confirm they always sent the header on every negotiated request. Cursor's
  trace has no network capture at all (client UI evidence only), so nothing about its header behavior
  was directly observed either way — the only available evidence is that Cursor's calls completed
  successfully, which is consistent with (but does not prove) it having sent the header; this is
  recorded as an inference, not an observation. Either way, this defect does not itself cast doubt on
  those tuples' observed protocol behavior. That said, their required disposition against the new
  candidate differs by tuple, not a single
  blanket "reconfirm all three": **Codex CLI is `QUALIFIED`** against the invalidated candidate and
  needs reconfirmation against the new one, per spec §4.4; **Claude Code is `QUALIFIED`** against the
  invalidated candidate and likewise needs reconfirmation; **Cursor is `UNVERIFIED`**, not
  `QUALIFIED`, against the invalidated candidate (see
  `docs/release-validation/v0.4.2-client-traces/cursor.md` — a mandatory pre-client baseline was never
  captured, independent of this VS Code finding), so Cursor still needs its **first** contract-complete
  qualification against the new candidate, not a reconfirmation of one that never happened.
