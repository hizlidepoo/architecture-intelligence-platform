# Codex CLI — Actual-Client Trace (I3.3)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **QUALIFIED**

This tuple has been qualified twice, against two different (now-superseded) candidates, per spec
§4.4's requirement that a candidate-affecting transport fix be reconfirmed rather than carried forward
by assertion — neither prior candidate's invalidation had anything to do with Codex CLI's own traffic
(both were unrelated defects found via Claude Code's and VS Code's traffic, respectively; Codex CLI's
own negotiated traffic never exercised either code path). The most recent reconfirmation, against the
current `RELEASE_CANDIDATE_SHA`, is recorded first below; the original qualification against the first
invalidated candidate (`6461db6d51ee29e9c973e62b005aa84d5d95c077`) is preserved unedited under
"Historical record" further down.

## Reconfirmation against `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`

### Tuple identity

| Field | Value |
|---|---|
| Client family | Codex CLI |
| Client product | `codex-cli` |
| Client version | `0.154.0` |
| Extension/plugin | N/A — built in |
| OS | Linux 5.15.153.1-microsoft-standard-WSL2, x86_64 |
| Execution mode | WSL |
| Client location | Same host as AIP (localhost) |
| AIP location | Docker container, same host, published port `8000` |
| Network topology | Client (host, WSL) → `localhost:8000` (published port) → `architecture-intelligence` container |
| Configuration mechanism | `codex mcp add aip --url http://localhost:8000/mcp` (per `examples/mcp-clients/codex.md`), global scope (`~/.codex/config.toml`) |
| Transport | Streamable HTTP |
| Approval mode | `codex exec --skip-git-repo-check -s read-only` (non-interactive); no approval prompt was requested or reached — MCP tool calls are read-only network calls, not sandboxed shell commands, so they are not gated by the exec sandbox/approval system |
| Candidate SHA | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` |
| Returned `producer.build_revision` | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` (exact match, confirmed live in every tool response below) |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | `2025-06-18` (negotiated mode; client sends no `mcp-method`/`mcp-name` markers at any point) |
| Session IDs issued / used / reuse | None observed (no `mcp-session-id` header in any client process's traffic) |
| Qualification date | 2026-09-13 |

Configuration mechanism, official-docs re-verification, and model/provider are unchanged from the
original qualification (see Historical record below) and are not repeated in full here.

### Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`50862a352626ea38d2fbb36f2ff0ecfc667266d0`, captured before `codex mcp add`/`get` or any client
interaction. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

### Attempt record (spec §6.5/§6.6)

| Cycle | Attempt | Classification | Outcome |
|---|---|---|---|
| 1 | 1 | — | Full success on the first attempt, using the corrected invocation shape from the original qualification (`--skip-git-repo-check` included from the start this time): `codex exec --json --skip-git-repo-check -s read-only -C <scratch-dir> - < prompt.txt` (Appendix A.1 fixed prompt). Called `get_architecture_drift` then `get_evidence` twice (once per finding), using the exact `snapshot_id`/`evidence_refs` returned, and reported the AIP qualifications verbatim without reinterpreting `NOT_OBSERVED_IN_WINDOW`. |

One valid client attempt used, well within the LLM-mediated budget of 2 (spec §6.5). No
infrastructure-invalidated runs or client-control failures occurred at any point in this reconfirmation.

### Required successful protocol workflow (spec §6.8)

Evidence combines the `codex exec --json` structured event stream (for tool-call inputs/outputs) with
a passive `tcpdump` capture of the actual `POST /mcp` traffic on the loopback/bridge path (observational
only — no header/body/method inserted, rewritten, or simulated, per spec §6.14), cross-checked against
each other.

| # | Requirement | Evidence |
|---|---|---|
| 1 | Initialization/negotiation | Passive capture: `POST /mcp` with body `{"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"codex-mcp-client","title":"Codex","version":"0.154.0"}}}` → `200`, followed by `notifications/initialized` → `202`. Repeated identically in a second, independent client process (see Reconnect below). |
| 2 | Tool discovery | Passive capture: `POST /mcp` `{"method":"tools/list", ...}` → `200`, full tool schemas returned. |
| 3 | Exactly three AIP tools discovered | The `tools/list` response body names exactly `get_architecture_drift`, `get_evidence`, `get_service_dependencies` — no others. |
| 4 | `get_architecture_drift` | `codex exec` JSON stream: `mcp_tool_call` item, `server: aip`, `tool: get_architecture_drift`, `status: completed`, request `{"service_id":"service:order-service","observation_context":{"environment":"demo","window_start":"2026-08-26T00:00:00Z","window_end":"2026-08-27T00:00:00Z"}}`. |
| 5 | Deterministic structured drift result | Response `outcome: PARTIAL`; claims resolve to `queue:unused-q` → `NOT_OBSERVED_IN_WINDOW` and `service:legacypricingservice` (via `GET /pricing/{sku}`) → `OBSERVED_ONLY` — the exact spec §6.9 expected result. |
| 6 | `get_evidence` using returned `evidence_refs` | Two `mcp_tool_call` items, `tool: get_evidence`, each using an `evidence_refs` value taken verbatim from the drift response (`evidence:asyncapi:order-service`, `evidence:otel:demo:2026-08-26:bfae54276215`). Both `outcome: ANSWERED`, `missing_evidence_refs: []`. |
| 7 | Same snapshot used | All three tool calls carry `snapshot.snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | `codex exec` is one-shot: the process exits after its turn completes, closing its MCP connection. |
| 9 | Reconnect/reinitialize | A second, independent `codex exec` process (fresh prompt, fresh `thread_id`) performed its own `initialize` → `notifications/initialized` → `tools/list` sequence from scratch (identical shape to attempt 1's, confirmed in the same passive capture). |
| 10 | One read-only tool works after reconnect | That second process's `get_service_dependencies` call for `service:order-service` (same observation window) returned `outcome: PARTIAL` with 4 dependency claims (`unused-q` `NOT_OBSERVED_IN_WINDOW`, `legacypricingservice` `OBSERVED_ONLY`, `payment-service` `CONFIRMED`, `product-service` `CONFIRMED`) and `producer.build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` — again the exact candidate SHA. |

The passive capture also directly reconfirms the I3.3 fix still holds at this new candidate: every
client process's `initialize` handshake is preceded by an OAuth-discovery probe sequence
(`.well-known/oauth-protected-resource`, etc., all cleanly `404`/`405` — ordinary, harmless Codex CLI
behavior when no auth is configured, unrelated to either transport fix), and `mcp-protocol-version` is
present on every negotiated request Codex sends (32 occurrences across the capture) — Codex CLI's own
traffic shape is unaffected by, and does not exercise, either the I3.3 direct-marker or the I3.4
negotiated missing-header code paths.

### Sanitization statement (spec §6.15)

The passive capture and `codex exec --json` transcripts contained no authorization headers, bearer
tokens, cookies, API keys, refresh tokens, account identifiers, email addresses, personal user
identifiers, raw system prompts, or unrelated conversation/traffic (this AIP demo endpoint requires no
credential; `codex mcp add`/`get` confirmed `bearer_token_env_var: -`, `http_headers: -` throughout).
The `User-Agent: codex-mcp-client/0.154.0` string is retained as legitimate client-version evidence,
not a personal identifier. Raw `.pcap` and JSON transcript files were ephemeral, used only to produce
the excerpts and summaries in this trace, and were not retained beyond this qualification run. The
same statement applies to the Appendix A.2 UX observation's verbatim agent answer recorded below.

### Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`). This check was taken immediately after both processes covered by the protocol-qualification/reconnect evidence above (3 tool calls in attempt 1, 1 tool call in the reconnect process) and **before** the separate Appendix A.2 UX run below. |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged (`aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`), matching the pre-client snapshot `S`. Same timing as `revision_after`: taken before the UX run. |

As with the original qualification, this tuple's own fence/fixture recheck covers the protocol-
qualification/reconnect evidence above but **not** the separate Appendix A.2 UX run below (2 more tool
calls, executed afterward in its own fresh process). The release-level zero-write claim for that
portion rests on spec §6.12's explicit joint-support model (fence measurement + the automated
zero-write test suite), as before.

### Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh `codex exec` process/context, separate from the protocol-qualification run above, and
after this tuple's own post-client revision-fence/fixture recheck.

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Where visible:**

| | |
|---|---|
| Model/provider | `gpt-5.6-sol` (OpenAI) — Codex CLI's configured default model, `reasoning_effort = medium`; not overridden by `-m` in this run |
| Agent mode | `codex exec` (non-interactive), `-s read-only` sandbox |
| Tool approval mode | Non-interactive default; no approval prompt was requested or reached |

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

**Unedited observed outcome** (the agent's final message, verbatim — sanitization statement above):

> AIP found **2 architecture-drift findings** for `service:order-service` in `demo` during
> `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`.
>
> Snapshot: `aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`
>
> ### 1. Declared send to `queue:unused-q` was not observed
>
> - **Qualification:** `NOT_OBSERVED_IN_WINDOW`, with `SUFFICIENT` coverage.
> - **Resolved evidence:** `evidence:asyncapi:order-service`
>   - Type: declared AsyncAPI evidence
>   - Source: `examples/order-service/asyncapi.yaml`
>   - Establishes that `service:order-service` `SENDS` to `queue:unused-q`.
>   - It also establishes that the queue carries `message:UnusedMessage`, conforming to
>     `schema:UnusedMessage`.
> - **What AIP established:** The direct asynchronous dependency on `queue:unused-q` is declared, and
>   AIP classified it as not observed during the specified window with sufficient observation
>   coverage.
> - **Boundary:** AIP did **not** establish why no activity was observed, whether the queue is unused
>   generally, or which service consumes from it. AIP explicitly reported that no single consumer
>   service was evidenced, so it retained the queue itself as the direct target
>   (`DIRECT_TARGET_FALLBACK`).
>
> Claim: `aip:claim:v1:ca0dd73ba391552edd6d2cc06cddd919a8af97f362cdb47392e78325219fd612`
>
> ### 2. Observed call to `LegacyPricingService` had no declared counterpart
>
> - **Qualification:** `OBSERVED_ONLY`.
> - **Resolved evidence:**
>   - `evidence:otel:demo:2026-08-26:bfae54276215` establishes that `service:order-service` called
>     `GET /pricing/{sku}`.
>   - `evidence:otel:demo:2026-08-26:29d4976aeaf9` establishes that `service:legacypricingservice`
>     provides that operation.
>   - Both are OpenTelemetry observations covering the requested window. Each reports one observation
>     at `2026-08-26T12:00:00.044222Z`, correlated using `CLIENT_SERVER`.
> - **What AIP established:** AIP resolved the observed synchronous HTTP dependency to
>   `service:legacypricingservice` and classified it as observed-only in this snapshot.
> - **Boundary:** AIP did **not** establish the request's success, payload, latency, business purpose,
>   deployment version, or whether the missing declaration was intentional. The evidence supports one
>   correlated observation, not a claim about call frequency beyond that observation.
>
> Claim: `aip:claim:v1:8c43c7b5ba7783da9b188afd0e28a72d0570d3a48a9772c5911ce8469e89bbd0`
>
> The drift query's overall outcome was `PARTIAL` solely because the consumer identity behind
> `queue:unused-q` could not be uniquely resolved. All three evidence references were successfully
> resolved using the same snapshot.

This is observational product evidence only, not a semantic release gate (spec §7.2).

### Disposition

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`.
- Same-snapshot, reconnect, and exact-tool-count requirements independently confirmed via passive
  capture, not inferred from the `codex exec` transcript alone. Zero-write confirmed by direct
  revision-fence measurement for the protocol-qualification/reconnect evidence, and by the automated
  zero-write test suite for the separate UX run's two calls.
- One clean valid attempt, no cycle failures — the `--skip-git-repo-check` lesson from the original
  qualification (see Historical record) was applied from the start this time.
- This tuple's traffic does not exercise either the I3.3 direct-marker allowlist or the I3.4
  negotiated missing-header fallback code path (see the protocol-workflow note above); this
  reconfirmation exists to satisfy spec §4.4's candidate-affecting-change requirement, not because
  either fix was expected to change Codex CLI's own observed behavior — and it did not.

---

## Historical record: original qualification against invalidated candidate `6461db6d51ee29e9c973e62b005aa84d5d95c077`

Preserved unedited below, for the same reason the Claude Code trace preserves its own historical
record: earlier valid-client evidence is not hidden by only reporting the latest reconfirmation.

### Tuple identity (as recorded at the time)

| Field | Value |
|---|---|
| Client family | Codex CLI |
| Client product | `codex-cli` |
| Client version | `0.154.0` |
| Extension/plugin | N/A — built in |
| OS | Linux 5.15.153.1-microsoft-standard-WSL2, x86_64 |
| Execution mode | WSL |
| Client location | Same host as AIP (localhost) |
| AIP location | Docker container, same host, published port `8000` |
| Network topology | Client (host, WSL) → `localhost:8000` (published port) → `architecture-intelligence` container |
| Configuration mechanism | `codex mcp add aip --url http://localhost:8000/mcp` (per `examples/mcp-clients/codex.md`), global scope (`~/.codex/config.toml`) |
| Transport | Streamable HTTP |
| Approval mode | `codex exec -s read-only` (non-interactive); no approval prompt was requested or reached — MCP tool calls are read-only network calls, not sandboxed shell commands, so they are not gated by the exec sandbox/approval system |
| Candidate SHA | `6461db6d51ee29e9c973e62b005aa84d5d95c077` (**INVALIDATED** — see the rc.2 candidate-preparation record) |
| Returned `producer.build_revision` | `6461db6d51ee29e9c973e62b005aa84d5d95c077` (exact match, confirmed live in every tool response below) |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | `2025-06-18` (negotiated mode; client sends no `mcp-method`/`mcp-name` markers at any point) |
| Session IDs issued / used / reuse | None observed (no `mcp-session-id` header in either client process's traffic) |
| Qualification date | 2026-09-13 |

### Configuration re-verification (spec §6.4)

| | |
|---|---|
| Official source | <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> |
| Verification date | 2026-09-13 (this run) |
| Result | PASS — the official docs page does document a `--url` flag on `codex mcp add` (`codex mcp add example --url https://mcp.example.com --oauth-client-id my-client`, shown under the OAuth pre-registered-client-ID section), and the installed `codex-cli 0.154.0`'s own `--help` documents the same flag (`--url <URL>  URL for a streamable HTTP MCP server`) independent of OAuth. `examples/mcp-clients/codex.md`'s claim is accurate. A narrower distinction worth noting: the docs page's only worked `--url` example includes `--oauth-client-id`; it does not show the simpler unauthenticated form used here (`--url` alone, no OAuth flags) as its own example. This qualification run used and confirmed the unauthenticated form works exactly as `--help` describes — not release-blocking, and not a documentation defect (an initial verification pass using a web-summarization tool missed the OAuth-section example on the first two attempts; corrected here by inspecting the raw page source directly). |

### Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

### Attempt record (spec §6.5/§6.6)

| Cycle | Attempt | Classification | Outcome |
|---|---|---|---|
| 1 | 1 | `CLIENT_CONTROL_FAILURE` | `codex exec --json -s read-only -C <scratch-dir> - < prompt.txt` (no `--skip-git-repo-check`) refused to start: `"Not inside a trusted directory and --skip-git-repo-check was not specified."` AIP/demo/network/fixture prerequisites were healthy at that moment (the server was up and serving, confirmed by the very next attempt succeeding against it unmodified); the official client itself could not issue the required call, matching §6.6's `CLIENT_CONTROL_FAILURE` definition exactly. This is itself a **valid client attempt** (§6.5's definition turns on prerequisite health, not on which failure mode occurs) that **fails cycle 1's tuple** outright. |
| 2 | 1 | — | Configuration corrected — the invocation was missing the required `--skip-git-repo-check` flag because the working directory used for `codex exec` was a plain scratch directory outside any git repository, not because of any AIP/server/fixture problem. Qualification was restarted as a fresh cycle with the corrected invocation: `codex exec --json --skip-git-repo-check -s read-only -C <scratch-dir> - < prompt.txt` (Appendix A.1 fixed prompt). Full success: called `get_architecture_drift` then `get_evidence` twice (once per finding), using the exact `snapshot_id`/`evidence_refs` returned, and reported the AIP qualifications verbatim without reinterpreting `NOT_OBSERVED_IN_WINDOW`. |

Cycle 1's attempt never reached AIP, the fixture, or the client's MCP subsystem at all (it failed at
Codex's own local trust-gate before opening any network connection), so the pre-client state recorded
above (§6.2/§6.3, taken once before cycle 1 started) remained valid for cycle 2 unmodified — no
re-baseline was needed. Recorded per cycle, not aggregated away: **cycle 1 consumed one valid attempt
and failed** (`CLIENT_CONTROL_FAILURE`); **after the recorded configuration correction, cycle 2
consumed one valid attempt and qualified**. Two valid client attempts total across both cycles, each
individually within the LLM-mediated per-cycle budget of 2 (spec §6.5) — cycle 1 never needed a second
attempt within itself (it failed outright on its first), and cycle 2 succeeded on its first. No
infrastructure-invalidated runs occurred at any point (cycle 1's failure is a client-control failure,
not an AIP/server/network/fixture prerequisite failure, so §6.5's separate infrastructure-retry-budget
accounting does not apply to it).

### Required successful protocol workflow (spec §6.8)

Evidence combines the `codex exec --json` structured event stream (for tool-call inputs/outputs) with
a passive `tcpdump` capture of the actual `POST /mcp` traffic on the loopback/bridge path (observational
only — no header/body/method inserted, rewritten, or simulated, per spec §6.14), cross-checked against
each other.

| # | Requirement | Evidence |
|---|---|---|
| 1 | Initialization/negotiation | Passive capture: `POST /mcp` with body `{"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"codex-mcp-client","title":"Codex","version":"0.154.0"}}}` → `200`, followed by `notifications/initialized` → `202`. Repeated identically in two further, independent client processes (see Reconnect below). |
| 2 | Tool discovery | Passive capture: `POST /mcp` `{"method":"tools/list", ...}` → `200`, full tool schemas returned. |
| 3 | Exactly three AIP tools discovered | The `tools/list` response body names exactly `get_architecture_drift`, `get_evidence`, `get_service_dependencies` — no others. |
| 4 | `get_architecture_drift` | `codex exec` JSON stream: `mcp_tool_call` item, `server: aip`, `tool: get_architecture_drift`, `status: completed`, request `{"service_id":"service:order-service","observation_context":{"environment":"demo","window_start":"2026-08-26T00:00:00Z","window_end":"2026-08-27T00:00:00Z"}}`. |
| 5 | Deterministic structured drift result | Response `outcome: PARTIAL`; claims resolve to `queue:unused-q` → `NOT_OBSERVED_IN_WINDOW` and `service:legacypricingservice` (via `GET /pricing/{sku}`) → `OBSERVED_ONLY` — the exact spec §6.9 expected result. |
| 6 | `get_evidence` using returned `evidence_refs` | Two `mcp_tool_call` items, `tool: get_evidence`, each using an `evidence_refs` value taken verbatim from the drift response (`evidence:otel:demo:2026-08-26:bfae54276215`, `evidence:asyncapi:order-service`). Both `outcome: ANSWERED`, `missing_evidence_refs: []`. |
| 7 | Same snapshot used | All three tool calls carry `snapshot.snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | `codex exec` is one-shot: the process exits after its turn completes, closing its MCP connection. |
| 9 | Reconnect/reinitialize | Two further, independent `codex exec` processes (fresh prompts, fresh `thread_id`s each) each performed their own `initialize` → `notifications/initialized` → `tools/list` sequence from scratch (identical shape to cycle 2's, confirmed in the same passive capture): the first (`get_service_dependencies`, malformed `service_id` on its first call, corrected on a second call within the same process — 2 tool calls, both `status: completed`) at ~9.5-13.4s into the capture, the second (single well-formed `get_service_dependencies` call) at ~41.8-53.4s into the capture. |
| 10 | One read-only tool works after reconnect | The second reconnect process's `get_service_dependencies` call for `service:order-service` (same observation window) returned `outcome: PARTIAL` with 4 dependency claims (`unused-q` `NOT_OBSERVED_IN_WINDOW`, `legacypricingservice` `OBSERVED_ONLY`, `payment-service` `CONFIRMED`, `product-service` `CONFIRMED`) and `producer.build_revision = 6461db6d51ee29e9c973e62b005aa84d5d95c077` — again the exact candidate SHA. (The first reconnect process's corrected call also succeeded, returning `NOT_ANSWERED`/`OBSERVATION_CONTEXT_REQUIRED` for a call that omitted the required observation context — a valid, well-formed AIP business response, not a transport failure; not used as the primary reconnect citation only because it demonstrates a prompt-authoring gap on the operator's side rather than a clean positive result.) |

### Sanitization statement (spec §6.15)

The passive capture and `codex exec --json` transcripts contained no authorization headers, bearer
tokens, cookies, API keys, refresh tokens, account identifiers, email addresses, personal user
identifiers, raw system prompts, or unrelated conversation/traffic (this AIP demo endpoint requires no
credential; `codex mcp add`/`get` confirmed `bearer_token_env_var: -`, `http_headers: -` throughout).
The `User-Agent: codex-mcp-client/0.154.0` string is retained as legitimate client-version evidence,
not a personal identifier. Raw `.pcap` and JSON transcript files were ephemeral, used only to produce
the excerpts and summaries in this trace, and were not retained beyond this qualification run. The
same statement applies to the Appendix A.2 UX observation's verbatim agent answer recorded below: it
contains only architecture-fact content returned by AIP's own tools, with no headers, tokens,
identifiers, or unrelated content of any kind.

### Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`). This check was taken immediately after the three processes covered by the protocol-qualification/reconnect evidence above (cycle 2's successful process — 3 tool calls; the two reconnect processes — 2 + 1 tool calls; 6 tool calls total across 3 processes) and **before** the separate Appendix A.2 UX run below. |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged (`aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`), matching the pre-client snapshot `S`. Same timing as `revision_after`: taken before the UX run. |

This tuple's own fence/fixture recheck therefore covers cycle 1's failed attempt (no calls reached
AIP) and cycle 2's full protocol-qualification + reconnect evidence, but **not** the separate Appendix
A.2 UX run below, which was executed afterward in its own fresh process (2 more tool calls: one
`get_architecture_drift`, one `get_evidence` resolving all three references in a single call) and was
not independently re-fenced. This tuple's zero-write finding is therefore stated precisely as covering
the protocol-qualification/reconnect portion, not the whole trace file end-to-end. The release-level
zero-write claim as a whole is not weakened by this: per spec §6.12, it is "supported jointly by
actual-client revision fence unchanged AND automated direct/negotiated zero-write tests" — the UX
run's two calls used only `get_architecture_drift` and `get_evidence`, both already proven zero-write
for every direct/negotiated routing path by `tests/integration/test_mcp_i1_zero_write_completion_gate.py`
independent of which client issues the call.

### Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh `codex exec` process/context, separate from the protocol-qualification runs above, and
after this tuple's own post-client revision-fence/fixture recheck (see note above).

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Where visible:**

| | |
|---|---|
| Model/provider | `gpt-5.6-sol` (OpenAI) — Codex CLI's configured default model, `reasoning_effort = medium`; not overridden by `-m` in this run |
| Agent mode | `codex exec` (non-interactive), `-s read-only` sandbox |
| Tool approval mode | Non-interactive default; no approval prompt was requested or reached — MCP tool calls are not gated by the exec sandbox/approval system |

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

**Unedited observed outcome** (the agent's final message, verbatim — sanitization statement above):

> AIP found **2 architecture-drift claims** for `service:order-service` in `demo` during
> `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`.
>
> Snapshot: `aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`
>
> All three evidence references resolved successfully against this same snapshot.
>
> ### 1. Declared send to `queue:unused-q` was not observed
>
> - **Qualification:** `NOT_OBSERVED_IN_WINDOW`
> - **Coverage:** `SUFFICIENT`
> - **Relationship:** `OrderService` → `SENDS` → `unused-q`
> - **Destination resolution:** `DIRECT_TARGET_FALLBACK`
>
> **Why it qualified**
>
> AIP has declared AsyncAPI evidence that `service:order-service` sends messages to `queue:unused-q`.
> With sufficient observational coverage, AIP found no corresponding observation during the requested
> window.
>
> **Resolved evidence**
>
> `evidence:asyncapi:order-service`:
>
> - Type: declared
> - Source: `examples/order-service/asyncapi.yaml`
> - Supports:
>   - `service:order-service SENDS queue:unused-q`
>   - `queue:unused-q CARRIES message:UnusedMessage`
>   - `message:UnusedMessage CONFORMS_TO schema:UnusedMessage`
>
> **What AIP established**
>
> - The snapshot declares that OrderService sends to `unused-q`.
> - That dependency was not observed in the specified environment and window.
> - Observational coverage was sufficient for the `NOT_OBSERVED_IN_WINDOW` qualification.
>
> **What AIP did not establish**
>
> - That the dependency is dead, broken, or safe to remove.
> - That no message was ever sent outside this window.
> - Which service consumes `unused-q`. AIP explicitly reports no single evidenced consumer and
>   retains the queue itself as the direct target.
>
> ---
>
> ### 2. Observed call to `LegacyPricingService` lacks a matching declaration
>
> - **Qualification:** `OBSERVED_ONLY`
> - **Relationship:** `OrderService` → `CALLS` → `LegacyPricingService`
> - **Delivery:** synchronous HTTP through `GET /pricing/{sku}`
> - **Destination resolution:** `RESOLVED_SERVICE`
>
> **Why it qualified**
>
> OpenTelemetry evidence shows OrderService calling `GET /pricing/{sku}`, and separate correlated
> evidence resolves that operation to `LegacyPricingService`. AIP's snapshot contains no matching
> declared dependency, so the relationship is classified as observed-only.
>
> **Resolved evidence**
>
> `evidence:otel:demo:2026-08-26:bfae54276215`:
>
> - Supports `service:order-service CALLS operation:service:legacypricingservice:GET:/pricing/{sku}`
> - Observation count: `1`
> - First/last seen: `2026-08-26T12:00:00.044222Z`
> - Correlation: `CLIENT_SERVER`
>
> `evidence:otel:demo:2026-08-26:29d4976aeaf9`:
>
> - Supports `service:legacypricingservice PROVIDES operation:service:legacypricingservice:GET:/pricing/{sku}`
> - Observation count: `1`
> - Same timestamp and correlation mode
>
> **What AIP established**
>
> - One correlated client/server observation connects OrderService to the pricing operation.
> - The operation is evidenced as provided by `LegacyPricingService`.
> - No matching declared dependency exists in this AIP snapshot.
>
> **What AIP did not establish**
>
> - Whether the call was authorized, intentional, erroneous, or policy-violating.
> - Whether it occurred more than once; the evidence records only one observation.
> - Which deployed service version made or served the call; `service_version` is absent.
> - Whether the dependency exists in other environments or time windows.
>
> AIP marked the overall drift response `PARTIAL` solely because the consumer identity behind
> `unused-q` could not be resolved without guessing.

This is observational product evidence only, not a semantic release gate (spec §7.2); the outcome
above happens to be a strong one, but the UX observation's contract-complete recording — not that
quality — is what §7.2 requires.

### Disposition (as recorded at the time)

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 6461db6d51ee29e9c973e62b005aa84d5d95c077`.
- Same-snapshot, reconnect, and exact-tool-count requirements independently confirmed via passive
  capture, not inferred from the `codex exec` transcript alone. Zero-write is confirmed for cycle 1's
  failed attempt and cycle 2's full protocol-qualification/reconnect evidence by direct revision-fence
  measurement, and for the separate Appendix A.2 UX run's two calls by the automated zero-write test
  suite (both use only already-proven-zero-write tools) — see the Post-client state note above.
- Cycle 1's `CLIENT_CONTROL_FAILURE` and cycle 2's success are both recorded in the attempt table; the
  earlier failure is not aggregated away by only reporting cycle 2.
- Configuration re-verification confirms `examples/mcp-clients/codex.md`'s `--url` claim is accurate
  against current official documentation; see the narrower distinction recorded above (OAuth-flagged
  example vs. the simpler unauthenticated form used here).
