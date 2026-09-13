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
| Result | The `--url` flag genuinely exists and works in the installed `codex-cli 0.154.0` (`codex mcp add --help` documents it: `--url <URL>  URL for a streamable HTTP MCP server`, and it was used successfully below). **Finding**: the official docs page's own prose does not show a worked `codex mcp add --url ...` example — its only CLI example is for a stdio server (`codex mcp add context7 -- npx ...`); the page's HTTP-server section only shows the `url` field inside `config.toml`. `examples/mcp-clients/codex.md`'s current claim that "the official docs ... document a `--url` flag" is broader than what the docs page's prose actually shows; the flag is real and correctly documented in the CLI's own `--help`, which is what this qualification run relies on. Not release-blocking (the flag is genuine, not invented, and worked exactly as documented by `--help`), but worth a small follow-up correction to that guide's wording. |

## Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

## Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 1 | — | Full success on the first valid attempt: `codex exec` (Appendix A.1 fixed prompt) called `get_architecture_drift` then `get_evidence` twice (once per finding), using the exact `snapshot_id`/`evidence_refs` returned, and reported the AIP qualifications verbatim without reinterpreting `NOT_OBSERVED_IN_WINDOW`. |

One valid client attempt used, within the LLM-mediated budget of 2 (spec §6.5). No infrastructure-invalidated runs occurred (one earlier local `codex exec` invocation failed with "Not inside a trusted directory and `--skip-git-repo-check` was not specified" *before* any request reached AIP or the client's MCP subsystem — a CLI invocation-argument mistake on the operator's side, not an AIP/network/fixture prerequisite failure, so it is not itself an "infrastructure-invalidated run" under §6.5's definition and does not consume any budget).

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
the excerpts and summaries in this trace, and were not retained beyond this qualification run.

## Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`). Zero writes across the entire tuple (initialize/discovery, both `codex exec` processes, all five tool calls). |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged (`aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`), matching the pre-client snapshot `S`. |

## Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh `codex exec` process/context, separate from the protocol-qualification runs above.

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Observed outcome (unedited in substance):** Codex called `get_architecture_drift` for the same
service/environment/window, then resolved all evidence references against the returned snapshot, and
reported both findings with an explicit "what AIP established" / "what AIP did not establish" split
for each — e.g. for `unused-q`: established that the declared send exists and was not observed in the
window with sufficient coverage; explicitly *not* established that the dependency is dead, unused, or
that no consumer exists (AIP's own `DIRECT_TARGET_FALLBACK` limitation was surfaced, not glossed over).
For `LegacyPricingService`: established one correlated OpenTelemetry observation and the absence of a
matching declaration; explicitly *not* established authorization intent, call frequency beyond the one
observation, or applicability outside this window/environment. No fact was asserted beyond what the
tool responses actually returned. This is observational product evidence only, not a semantic release
gate (spec §7.2).

## Disposition

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 6461db6d51ee29e9c973e62b005aa84d5d95c077`.
- Zero-write, same-snapshot, reconnect, and exact-tool-count requirements all independently confirmed
  via passive capture, not inferred from the `codex exec` transcript alone.
- Minor non-blocking documentation finding recorded above (the official Codex docs page's prose does
  not itself show a `--url` example, unlike `examples/mcp-clients/codex.md`'s current claim) — does not
  affect this tuple's result, since the flag is genuine and functioned exactly as used.
