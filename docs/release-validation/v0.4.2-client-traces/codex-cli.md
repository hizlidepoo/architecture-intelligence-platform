# Codex CLI — Actual-Client Trace (I3.3)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **QUALIFIED**

This tuple was first qualified against the pre-fix candidate `71e2d8b954fa92430723fced302baa3666255397`
(see `docs/release-validation/v0.4.2-client-traces/claude-code.md`'s Disposition section) but never
committed as its own trace file. That candidate was invalidated by an unrelated Claude Code
transport-layer defect (fixed by the ADR 0014 amendment) that Codex CLI's traffic never exercised —
Codex CLI is a **negotiated-mode** client and never sends the `mcp-method`/`mcp-name` direct-mode
markers the defect required. Per spec §4.4, the tuple is nonetheless reconfirmed here in full against
the new, post-fix `RELEASE_CANDIDATE_SHA` rather than carried forward by assertion.

## Tuple identity

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
| Candidate SHA | `6461db6d51ee29e9c973e62b005aa84d5d95c077` |
| Returned `producer.build_revision` | `6461db6d51ee29e9c973e62b005aa84d5d95c077` (exact match, confirmed live in every tool response below) |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | `2025-06-18` (negotiated mode; client sends no `mcp-method`/`mcp-name` markers at any point) |
| Session IDs issued / used / reuse | None observed (no `mcp-session-id` header in either client process's traffic) |
| Qualification date | 2026-09-13 |

## Configuration re-verification (spec §6.4)

| | |
|---|---|
| Official source | <https://learn.chatgpt.com/docs/extend/mcp?surface=cli> |
| Verification date | 2026-09-13 (this run) |
| Result | PASS — the official docs page does document a `--url` flag on `codex mcp add` (`codex mcp add example --url https://mcp.example.com --oauth-client-id my-client`, shown under the OAuth pre-registered-client-ID section), and the installed `codex-cli 0.154.0`'s own `--help` documents the same flag (`--url <URL>  URL for a streamable HTTP MCP server`) independent of OAuth. `examples/mcp-clients/codex.md`'s claim is accurate. A narrower distinction worth noting: the docs page's only worked `--url` example includes `--oauth-client-id`; it does not show the simpler unauthenticated form used here (`--url` alone, no OAuth flags) as its own example. This qualification run used and confirmed the unauthenticated form works exactly as `--help` describes — not release-blocking, and not a documentation defect (an initial verification pass using a web-summarization tool missed the OAuth-section example on the first two attempts; corrected here by inspecting the raw page source directly). |

## Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

## Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 0 | `CLIENT_CONTROL_FAILURE` | `codex exec --json -s read-only -C <scratch-dir> - < prompt.txt` (no `--skip-git-repo-check`) refused to start: `"Not inside a trusted directory and --skip-git-repo-check was not specified."` AIP/demo/network/fixture prerequisites were healthy at that moment (the server was up and serving, confirmed by the very next attempt succeeding against it unmodified); the official client itself could not issue the required call, matching §6.6's `CLIENT_CONTROL_FAILURE` definition exactly. Per §6.5 (Deterministic client control) / the general failure-taxonomy rule, this **fails the tuple** as of this attempt. |
| 1 (fresh cycle, after correction) | — | Configuration corrected — the invocation was missing the required `--skip-git-repo-check` flag because the working directory used for `codex exec` was a plain scratch directory outside any git repository, not because of any AIP/server/fixture problem. Qualification was restarted as a fresh cycle with the corrected invocation: `codex exec --json --skip-git-repo-check -s read-only -C <scratch-dir> - < prompt.txt` (Appendix A.1 fixed prompt). Full success: called `get_architecture_drift` then `get_evidence` twice (once per finding), using the exact `snapshot_id`/`evidence_refs` returned, and reported the AIP qualifications verbatim without reinterpreting `NOT_OBSERVED_IN_WINDOW`. |

Attempt 0 never reached AIP, the fixture, or the client's MCP subsystem at all (it failed at Codex's own local trust-gate before opening any network connection), so the pre-client state recorded above (§6.2/§6.3, taken once before either invocation) remains valid for attempt 1 unmodified — no re-baseline was needed. One valid client attempt (attempt 1) is consumed, within the LLM-mediated budget of 2 (spec §6.5). No infrastructure-invalidated runs occurred (attempt 0 is a client-control failure, not an AIP/server/network/fixture prerequisite failure, so it does not fall under §6.5's infrastructure-retry-budget accounting either).

## Required successful protocol workflow (spec §6.8)

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
| 6 | `get_evidence` using returned `evidence_refs` | Two `mcp_tool_call` items, `tool: get_evidence`, each using an `evidence_refs` value taken verbatim from the drift response (`evidence:otel:demo:2026-08-26:bfae54276215`, `evidence:asyncapi:order-service`). Both `outcome: ANSWERED`, `missing_evidence_refs: []`. |
| 7 | Same snapshot used | All three tool calls carry `snapshot.snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | `codex exec` is one-shot: the process exits after its turn completes, closing its MCP connection. |
| 9 | Reconnect/reinitialize | A second, independent `codex exec` process (fresh prompt, fresh `thread_id`) performed its own `initialize` → `notifications/initialized` → `tools/list` sequence from scratch (identical shape to attempt 1's, confirmed in the same passive capture, ~41s after the first sequence). |
| 10 | One read-only tool works after reconnect | That second process's `get_service_dependencies` call for `service:order-service` (same observation window) returned `outcome: PARTIAL` with 4 dependency claims (`unused-q` `NOT_OBSERVED_IN_WINDOW`, `legacypricingservice` `OBSERVED_ONLY`, `payment-service` `CONFIRMED`, `product-service` `CONFIRMED`) and `producer.build_revision = 6461db6d51ee29e9c973e62b005aa84d5d95c077` — again the exact candidate SHA. |

## Sanitization statement (spec §6.15)

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

## Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`). Zero writes across the entire tuple (initialize/discovery, both `codex exec` processes, all five tool calls). |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged (`aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`), matching the pre-client snapshot `S`. |

## Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh `codex exec` process/context, separate from the protocol-qualification runs above.

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

## Disposition

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 6461db6d51ee29e9c973e62b005aa84d5d95c077`.
- Zero-write, same-snapshot, reconnect, and exact-tool-count requirements all independently confirmed
  via passive capture, not inferred from the `codex exec` transcript alone.
- Configuration re-verification confirms `examples/mcp-clients/codex.md`'s `--url` claim is accurate
  against current official documentation; see the narrower distinction recorded above (OAuth-flagged
  example vs. the simpler unauthenticated form used here).
