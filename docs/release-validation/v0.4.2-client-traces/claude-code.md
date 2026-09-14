# Claude Code — Actual-Client Trace (I3.3)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **QUALIFIED**

This tuple's history in one line: **FAILED** (`71e2d8b...`, transport hang — see Historical record
further down) → **QUALIFIED** (`6461db6d...`, now itself invalidated for an unrelated VS Code defect —
see the next Historical record) → **QUALIFIED** (current `RELEASE_CANDIDATE_SHA`, recorded first
below, corrected twice — see that section). Per spec §6.5, no earlier valid-client result — failure or
success — is hidden by only reporting the latest one; both prior records are preserved unedited further
down.

## Reconfirmation against `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`

This candidate includes the I3.4 negotiated-mode missing-header fix (ADR 0014's second "Amendment"
section), on top of the I3.3 direct-marker allowlist fix this tuple already qualified against. Claude
Code's own traffic does not exercise the I3.4 code path either (it always sends
`MCP-Protocol-Version` on negotiated follow-ups, confirmed again below), so this reconfirmation exists
to satisfy spec §4.4's candidate-affecting-change requirement, not because the new fix was expected to
change Claude Code's own observed behavior.

**Correction, PR #152 review:** an earlier version of this section did not capture
`producer.build_revision` from Claude Code's own traffic before its session transcripts were deleted,
and incorrectly relied on Codex CLI's cross-server confirmation as a stand-in — the review correctly
pointed out that server identity is not the same as proof of what Claude Code itself received, and
spec §6.8/§6.13 require the latter. The tuple was re-run in full (fresh fixture, fresh pre-client
baseline) with `producer.build_revision` extracted directly from Claude Code's own session transcripts
*before* their deletion.

**Second correction (self-identified while building the I3.5 cross-client matrix):** the corrected
run above still had the same defect PR #153 review later caught in Cursor's trace: its `get_evidence`
call for Finding 2 combined the claim's own `evidence_refs` with a separate `resolution_evidence_refs`
entry into one call, deviating from the fixed Appendix A.1 prompt's "using exactly the evidence_refs"
instruction. This predates the Cursor review that established the strict per-finding reading and was
never independently re-checked against it. For consistency with the standard already applied to
Cursor and VS Code, that run is reclassified below as a failed valid attempt
(`MODEL_TOOL_SELECTION_FAILURE`, cycle 1), and a fresh cycle 2 was run using only each finding's own
`evidence_refs`, confirmed directly in the session transcript.

### Tuple identity

| Field | Value |
|---|---|
| Client family | Claude Code |
| Client product | Claude Code CLI |
| Client version | `2.1.270` |
| Extension/plugin | N/A — built in |
| OS | Linux 5.15.153.1-microsoft-standard-WSL2, x86_64 |
| Execution mode | WSL |
| Client location | Same host as AIP (localhost) |
| AIP location | Docker container, same host, published port `8000` |
| Network topology | Client (host, WSL) → `localhost:8000` (published port) → `architecture-intelligence` container |
| Configuration mechanism | `claude mcp add --transport http --scope local aip http://localhost:8000/mcp` (per `examples/mcp-clients/claude-code.md`), scope `local` |
| Transport | Streamable HTTP |
| Candidate SHA | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` |
| Returned `producer.build_revision` | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` — exact match, extracted directly from Claude Code's own session transcript (`tool_result` content) for every one of the 4 tool calls in cycle 2's qualifying attempt and reconnect, before the transcripts were deleted |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | Not independently captured for cycle 2 (no passive network capture was available in this environment for this redo — `tcpdump` requires elevated privileges not available here); the session transcript directly confirms tool discovery and correct three-tool behavior via successful `mcp__aip__*` tool calls in every process |
| Session IDs issued / used / reuse | Not independently captured for the same reason; consistent with every other client family's evidence that AIP's negotiated mode issues none |
| Qualification date | 2026-09-14 |

Approval behavior, configuration re-verification, and the `--allowedTools` methodology are unchanged
from the prior qualification (see Historical record below) and are not repeated in full here: same
`--allowedTools` invocation naming the three AIP tools, same `permission_denials: []`, same no
persisted-permission file created.

### Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`50862a352626ea38d2fbb36f2ff0ecfc667266d0`, captured before `claude mcp add`/`get` or any client
interaction. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`. This baseline covers both cycle 1 (below, reclassified) and cycle 2 — both ran
against the same continuous fixture instance, no teardown in between.

### Attempt record (spec §6.5/§6.6)

| Cycle | Attempt | Classification | Outcome |
|---|---|---|---|
| 1 | 1 | `MODEL_TOOL_SELECTION_FAILURE` (self-identified, second correction above) | `claude mcp add`/`get` succeeded (`✔ Connected`); `claude -p` (Appendix A.1 fixed prompt) called `get_architecture_drift` correctly, then for Finding 2 issued a `get_evidence` call combining the claim's own `evidence_refs` (`evidence:otel:demo:2026-08-26:bfae54276215`) with its `resolution_evidence_refs` entry (`evidence:otel:demo:2026-08-26:29d4976aeaf9`) — deviating from the fixed prompt's "using exactly the evidence_refs" instruction. Prerequisites were healthy and the model otherwise executed correctly, so this is a valid attempt that failed on model tool selection, not infrastructure or client control. |
| 2 | 1 | — | Fresh `claude -p` process, same fixed Appendix A.1 prompt. Called `get_architecture_drift`, then issued two separate `get_evidence` calls, each using only that finding's own `evidence_refs` (Finding 1: `["evidence:asyncapi:order-service"]`; Finding 2: `["evidence:otel:demo:2026-08-26:bfae54276215"]`, no `resolution_evidence_refs`) — confirmed directly in the session transcript. The final report even explains why `resolution_evidence_refs` was not separately fetched: "outside the... scope you specified, which names the claim's `evidence_refs` field." `producer.build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` confirmed in the transcript for the drift call and both `get_evidence` calls. |

Per §6.6, one `MODEL_TOOL_SELECTION_FAILURE` on the LLM-mediated path permits exactly one further valid
attempt, which cycle 2 is. Two valid client attempts total, within the per-cycle budget of 2 (spec
§6.5); no infrastructure-invalidated runs occurred.

### Required successful protocol workflow (spec §6.8)

This table describes cycle 2 (the qualifying attempt) and its own reconnect. Evidence is cycle 2's own
`claude -p --output-format json` session transcript, read directly for both tool-call inputs and
outputs (including `producer.build_revision`) before deletion — no passive network capture was used
for this redo (see the Tuple identity note above), unlike the rest of this trace file.

| # | Requirement | Evidence |
|---|---|---|
| 1 | Initialization/negotiation | Session transcript: successful `mcp__aip__get_architecture_drift` tool call implies a completed `initialize`/`notifications/initialized` handshake (Claude Code's MCP client does not expose the raw handshake in the transcript directly; inferred from successful tool dispatch, not directly observed at the wire level for this redo). |
| 2 | Tool discovery | Session transcript: a `ToolSearch` call resolving `mcp__aip__get_architecture_drift,mcp__aip__get_evidence,mcp__aip__get_service_dependencies` succeeded, confirming all three tools were discovered. |
| 3 | Exactly three AIP tools discovered | The three tool names above are the only `mcp__aip__*` tools referenced or called anywhere in the transcript. |
| 4 | `get_architecture_drift` | `tool_use` `mcp__aip__get_architecture_drift`, request `{"service_id":"service:order-service","observation_context":{"environment":"demo","window_start":"2026-08-26T00:00:00Z","window_end":"2026-08-27T00:00:00Z"}}`; `tool_result` carries `"producer":{"name":"architecture-intelligence-platform","version":"0.4.2","build_revision":"50862a352626ea38d2fbb36f2ff0ecfc667266d0"}`. |
| 5 | Deterministic structured drift result | Response `outcome: PARTIAL`; claims resolve to `queue:unused-q` → `NOT_OBSERVED_IN_WINDOW` and `service:legacypricingservice` (via `GET /pricing/{sku}`) → `OBSERVED_ONLY` — the exact spec §6.9 expected result. |
| 6 | `get_evidence` using exactly the returned `evidence_refs` | Two separate `tool_use` calls, `mcp__aip__get_evidence`: `evidence_refs: ["evidence:asyncapi:order-service"]`, then `evidence_refs: ["evidence:otel:demo:2026-08-26:bfae54276215"]` — each finding's own `evidence_refs` only, no `resolution_evidence_refs`. Both `tool_result`s carry `build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`. |
| 7 | Same snapshot used | All three tool calls carry `snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | `claude -p` is one-shot: the process exits after its turn completes, closing its MCP connection. |
| 9 | Reconnect/reinitialize | A second, independent `claude -p` process (fresh session ID, fresh prompt) performed its own tool discovery and call from scratch. |
| 10 | One read-only tool works after reconnect | That second process's `mcp__aip__get_service_dependencies` call for `service:order-service` (same observation window) returned `outcome: PARTIAL` with 4 dependency claims (`unused-q` `NOT_OBSERVED_IN_WINDOW`, `legacypricingservice` `OBSERVED_ONLY`, `payment-service`/`product-service` `CONFIRMED`), same snapshot, `tool_result` carrying `build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`. |

This redo does not directly reconfirm the I3.3/I3.4 transport-level fixes at the wire level (no passive
capture was taken for cycle 1 or cycle 2); that reconfirmation stands on the original passive-capture
evidence recorded for this same candidate SHA when this trace was first corrected under PR #152 (both
processes' `server/discover` probe cleanly rejected, `mcp-protocol-version` present on every negotiated
follow-up) — unaffected by this evidence-refs-only correction, since neither fix's code path depends on
which `evidence_refs` a client passes to `get_evidence`.

### Sanitization statement (spec §6.15)

Same statement as the prior qualification: no authorization headers, bearer tokens, cookies, API
keys, refresh tokens, account identifiers, email addresses, personal identifiers, raw system prompts,
or unrelated content of any kind in the session transcripts (verified before extracting the
`producer`/tool-call excerpts quoted above). Session transcript files were ephemeral and deleted after
producing this trace.

### Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`). Measured directly via `read_revision_fence.py --json`, run after cycle 1, cycle 2, and the reconnect call, and **before** the separate Appendix A.2 UX run below. |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged, matching the pre-client snapshot `S`. |

Rechecked a second time after the separate Appendix A.2 UX run too (see that section below): `revision
= 9` still, fixture still `COMPLETE` — this correction's zero-write evidence covers the entire tuple
end to end (cycle 1, cycle 2, reconnect, and the UX run), all on one continuous fixture instance.

### Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh `claude -p` process/session, after cycle 2's protocol qualification and reconnect had
already completed.

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Where visible:** model `claude-sonnet-5` (not overridden), `claude -p` non-interactive with
`--allowedTools` pre-authorizing the three AIP tools, `permission_denials: []` (an initial attempt
without `--allowedTools` was blocked on approval before reaching AIP at all — a local client-control
quirk of non-interactive `-p` mode, not a classified attempt, since it never reached the server or any
AIP tool). `tool_result` content carried `build_revision = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`
for both tool calls in the successful run.

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

**Unedited observed outcome** (the agent's final message, verbatim — re-run for this correction so the
UX observation is correctly sequenced after cycle 2's success, per Appendix A.2's own "after protocol
qualification" ordering):

> Ran `get_architecture_drift` for `service:order-service` in `demo`, window
> `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`, then resolved every evidence ref it returned against
> the **same** `snapshot_id` (`aip:snapshot:v1:685a3415...`) via `get_evidence`.
>
> **Overall outcome: `PARTIAL`** (not `ANSWERED`) — AIP is itself flagging that one of the two claims
> below has an unresolved identity, per its `limitations` array. That partiality is a property of the
> answer, not something I'm inferring.
>
> Two drift claims were returned.
>
> ## Finding 1 — `order-service` → `queue:unused-q` (SENDS)
>
> **1. Qualification: `NOT_OBSERVED_IN_WINDOW`, coverage `SUFFICIENT`, destination_resolution
> `DIRECT_TARGET_FALLBACK`**
> AIP has a *declared* fact (from AsyncAPI) that order-service sends to `unused-q`, but found no OTel
> observation of that send occurring inside the 2026-08-26→27 window. `coverage: SUFFICIENT` means
> telemetry coverage in that window was judged adequate to detect the send if it had happened — so the
> absence is meaningful, not a blind spot. `DIRECT_TARGET_FALLBACK` means AIP could not resolve a
> downstream *consumer service* for this queue, so the drift object is the queue node itself rather
> than a resolved service.
>
> **2. Evidence resolved against the same snapshot**
> - `evidence:asyncapi:order-service` — `DECLARED`, source `ASYNCAPI`,
>   `examples/order-service/asyncapi.yaml`. Its `supports` list includes `SENDS service:order-service
>   -> queue:unused-q` (plus the unrelated `payment-q`/message-schema facts also declared in that same
>   file).
> - `resolution_evidence_refs` is empty — consistent with the stated limitation:
>   `"queue:unused-q has no single evidenced consumer service; retained as the direct queue target
>   rather than guessed."`
>
> **3. What AIP actually established**
> - OrderService is *declared* (spec-level, AsyncAPI) to send to `unused-q`.
> - In the specific 2026-08-26→27 demo window, with sufficient telemetry coverage, no OTel evidence of
>   that send was recorded.
> - AIP could not identify any service consuming `unused-q`, and explicitly declined to guess one.
>
> **4. Not established**
> AIP does not establish *why* the send wasn't observed (disabled feature, no traffic that day, broken
> code path, etc.), does not establish that the queue is unused in general (only in this window), and
> does not establish that the queue has no consumer at all — only that no consumer is evidenced.
>
> ## Finding 2 — `order-service` → `service:legacypricingservice` (CALLS)
>
> **1. Qualification: `OBSERVED_ONLY`, coverage `null`, destination_resolution `RESOLVED_SERVICE`**
> This is the inverse situation: there is *no declared* (OpenAPI/manifest) evidence anywhere that
> order-service calls `LegacyPricingService`, but AIP found a runtime OTel observation of that call
> inside the window. `RESOLVED_SERVICE` means AIP successfully resolved the call target operation
> (`GET /pricing/{sku}`) to a real provider service via separate OTel evidence. `coverage: null` — AIP
> reports no coverage judgment for this claim; I'm not filling that gap with an assumption either way.
>
> **2. Evidence resolved against the same snapshot**
> - `evidence:otel:demo:2026-08-26:bfae54276215` — `OBSERVED`/`OPENTELEMETRY`, bucket
>   `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`, `observation_count: 1`, `first_seen == last_seen ==
>   2026-08-26T12:00:00.044222Z`, `correlation_mode: CLIENT_SERVER`. Supports `CALLS
>   service:order-service -> operation:...legacypricingservice:GET:/pricing/{sku}`.
> - `evidence:otel:demo:2026-08-26:29d4976aeaf9` (this claim's `resolution_evidence_refs` entry) — same
>   window/timestamp, `observation_count: 1`. Supports `PROVIDES service:legacypricingservice ->
>   operation:...GET:/pricing/{sku}`. This is what let AIP resolve the call's target to
>   `LegacyPricingService` rather than leaving it as a bare operation.
>
> **3. What AIP actually established**
> - A single OTel-observed HTTP call from `order-service` to `GET /pricing/{sku}` occurred in the
>   window, correlated client↔server.
> - That operation's provider was independently observed (also once, same timestamp) to be
>   `LegacyPricingService`.
> - No declared/spec-level evidence supports this dependency anywhere in the current model — this is an
>   undeclared (runtime-only) dependency: real traffic to a service that isn't reflected in any
>   OpenAPI/manifest source.
>
> **4. Not established**
> `observation_count: 1` means exactly one recorded observation — AIP does not establish frequency,
> volume, or whether this is a recurring integration versus a one-off. It does not establish *why* the
> dependency is undeclared (missing manifest entry vs. new/shadow integration vs. stale spec), and does
> not establish criticality or intent. `coverage: null` means I cannot say whether telemetry coverage
> was sufficient to have caught this earlier or would catch its absence — that judgment simply isn't in
> the response.

This is observational product evidence only, not a semantic release gate (spec §7.2).

### Disposition

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`, on cycle 2's
  attempt (see Attempt record) — cycle 1 is `MODEL_TOOL_SELECTION_FAILURE` and superseded.
- `producer.build_revision` directly confirmed from Claude Code's own session transcripts for every
  tool call in cycle 2's qualifying attempt, reconnect, and the UX run — not inferred or
  cross-confirmed via another client, correcting the gap flagged in PR #152 review.
- The `get_evidence`-exactness gap self-identified while building the I3.5 cross-client matrix (see the
  second correction note above) is closed: cycle 2's two `get_evidence` calls each use only that
  finding's own `evidence_refs`.
- Zero-write confirmed by direct revision-fence measurement covering the entire tuple end to end
  (cycle 1, cycle 2, reconnect, and the UX run — rechecked a second time after it), all on one
  continuous fixture instance.
- Transport-level reconfirmation of the I3.3/I3.4 fixes stands on the original passive-capture evidence
  from this trace's first correction under PR #152 (see the protocol-workflow note above) — this
  redo's own evidence is session-transcript-only, since no passive capture was available in this
  environment for the redo.

---

## Historical record: requalification against invalidated candidate `6461db6d51ee29e9c973e62b005aa84d5d95c077`

Preserved unedited below. This candidate was itself later invalidated by an unrelated I3.4 VS Code
transport defect (see `docs/release-validation/v0.4.2-rc.2-candidate-preparation.md`); nothing in this
section's own findings about Claude Code was wrong or affected by that separate defect.

### Tuple identity

| Field | Value |
|---|---|
| Client family | Claude Code |
| Client product | Claude Code CLI |
| Client version | `2.1.270` |
| Extension/plugin | N/A — built in |
| OS | Linux 5.15.153.1-microsoft-standard-WSL2, x86_64 |
| Execution mode | WSL |
| Client location | Same host as AIP (localhost) |
| AIP location | Docker container, same host, published port `8000` |
| Network topology | Client (host, WSL) → `localhost:8000` (published port) → `architecture-intelligence` container |
| Configuration mechanism | `claude mcp add --transport http --scope local aip http://localhost:8000/mcp` (per `examples/mcp-clients/claude-code.md`), scope `local` |
| Transport | Streamable HTTP |
| Candidate SHA | `6461db6d51ee29e9c973e62b005aa84d5d95c077` (**INVALIDATED** — see the rc.2 candidate-preparation record) |
| Returned `producer.build_revision` | `6461db6d51ee29e9c973e62b005aa84d5d95c077` (exact match, confirmed live in every tool response below) |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | `2025-11-25` (negotiated mode, confirmed by passive capture) |
| Session IDs issued / used / reuse | None observed (no `mcp-session-id` header in any client process's traffic) |
| Qualification date | 2026-09-13 |

### Approval behavior (spec §6.7)

| Field | Value |
|---|---|
| Approval mode | `claude -p --allowedTools "mcp__aip__get_architecture_drift,mcp__aip__get_evidence,mcp__aip__get_service_dependencies"` — the three AIP tools pre-authorized by name for this non-interactive run |
| Approval requested | No — `permission_denials: []` in every run's JSON output |
| Manual approval required | No |
| Persistent allow enabled | No — `--allowedTools` is a process-local flag scoped to each individual `claude -p` invocation; confirmed no `.claude/settings*.json` or other persisted-permission file was created anywhere under the qualification worktree by any of the three `claude -p` runs, and `~/.claude.json` only ever gained the `claude mcp add`/`remove` server-registration entries, never a persisted tool-allow entry |

The same four values apply unchanged to the separate Appendix A.2 UX run below — the identical
`--allowedTools` invocation shape was used, and it likewise recorded `permission_denials: []`.

### Configuration re-verification (spec §6.4)

| | |
|---|---|
| Official source | <https://code.claude.com/docs/en/mcp> |
| Verification date | 2026-09-13 (this run) |
| Result | PASS — confirmed by inspecting the raw page source directly (not a web-summarization tool, per the lesson from this same qualification pass's Codex CLI trace): `claude mcp add --transport http <name> <url>` and `--scope local`/`--scope project`/`--scope user` are all present verbatim in the page's syntax-highlighted code blocks. Also confirmed live via `claude mcp add --help`: `-s, --scope <scope>  Configuration scope (local, user, or project) (default: "local")`. `examples/mcp-clients/claude-code.md`'s claim is accurate; no finding. |

### Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

### Attempt record (spec §6.5/§6.6)

| Cycle | Attempt | Classification | Outcome |
|---|---|---|---|
| 1 | 1 | — | Full success on the first valid attempt: `claude mcp add` (config write, no network), then `claude mcp get aip` / `claude mcp list` (the exact connectivity health-check that hung the pre-fix candidate) both completed instantly with `✔ Connected`; `claude -p` (Appendix A.1 fixed prompt) called `get_architecture_drift` then `get_evidence` twice (once per finding), using the exact `snapshot_id`/`evidence_refs` returned, and reported the AIP qualifications verbatim without reinterpreting `NOT_OBSERVED_IN_WINDOW`. |

One valid client attempt used, well within the LLM-mediated budget of 2 (spec §6.5). No
infrastructure-invalidated runs and no `CLIENT_CONTROL_FAILURE`/other classified failure occurred at
any point in this cycle.

**Methodology note, not a classified attempt:** before settling on `--allowedTools`, an initial
`claude -p --dangerously-skip-permissions ...` invocation was rejected by *this operating session's
own* Bash-tool permission classifier ("Create Unsafe Agents") before the `claude` binary was ever
invoked — no request of any kind reached the client under test, AIP, or the network. This is not a
`CLIENT_CONTROL_FAILURE` (contrast the Codex CLI trace's attempt 0, where the client-under-test itself
refused to start): here, the client-under-test was never started at all, so there is nothing to
classify against it. `--allowedTools` naming the exact three read-only AIP tools was used instead — a
narrower, more auditable approval configuration than a blanket permission bypass, not a weakening of
approval configuration after a failure (spec §6.7): it was the first and only approval configuration
ever used against the actual client.

### Required successful protocol workflow (spec §6.8)

Evidence combines each `claude -p --output-format json` run's own session transcript
(`~/.claude/projects/.../*.jsonl`, containing the exact tool-call inputs/outputs) with a passive
`tcpdump` capture of the real `POST /mcp` traffic on the loopback/bridge path (observational only — no
header/body/method inserted, rewritten, or simulated, per spec §6.14), cross-checked against each
other. The capture began before `claude mcp add`/`get`/`list` and continued through both `claude -p`
runs, so it independently proves the exact connectivity-check request sequence that hung the pre-fix
candidate now completes cleanly.

| # | Requirement | Evidence |
|---|---|---|
| 1 | Initialization/negotiation | Passive capture, present in every one of the 4 client processes captured (`claude mcp get`, `claude mcp list`, `claude -p` run 1, `claude -p` run 2): `POST /mcp` `initialize` (`protocolVersion: "2025-11-25"`) → `200`, then `notifications/initialized` → `202`. |
| 2 | Tool discovery | Passive capture: `POST /mcp` `tools/list` → `200` (32490-byte response, full tool schemas) in every process, immediately after `initialize`. |
| 3 | Exactly three AIP tools discovered | The `tools/list` response body names exactly `get_architecture_drift`, `get_evidence`, `get_service_dependencies` — no others; also confirmed via each session transcript's `ToolSearch` tool-reference results (Claude Code's own deferred-tool lookup, resolving `mcp__aip__get_architecture_drift`/`get_evidence`/`get_service_dependencies` by name). |
| 4 | `get_architecture_drift` | Session transcript (run 1): `tool_use` `mcp__aip__get_architecture_drift`, request `{"service_id":"service:order-service","observation_context":{"environment":"demo","window_start":"2026-08-26T00:00:00Z","window_end":"2026-08-27T00:00:00Z"}}`. |
| 5 | Deterministic structured drift result | Response `outcome: PARTIAL`; claims resolve to `queue:unused-q` → `NOT_OBSERVED_IN_WINDOW` and `service:legacypricingservice` (via `GET /pricing/{sku}`) → `OBSERVED_ONLY` — the exact spec §6.9 expected result. |
| 6 | `get_evidence` using returned `evidence_refs` | Two `tool_use` calls, `mcp__aip__get_evidence`, first with `evidence_refs: ["evidence:asyncapi:order-service"]`, second with `evidence_refs: ["evidence:otel:demo:2026-08-26:bfae54276215", "evidence:otel:demo:2026-08-26:29d4976aeaf9"]` — both taken verbatim from the drift response. Both `outcome: ANSWERED`. |
| 7 | Same snapshot used | All three tool calls (run 1) carry `snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | `claude -p` is one-shot: the process exits after its turn completes, closing its MCP connection. |
| 9 | Reconnect/reinitialize | A second, independent `claude -p` process (fresh session ID, fresh prompt) performed its own `initialize` → `notifications/initialized` → `tools/list` sequence from scratch (identical shape to run 1's, confirmed in the same passive capture). |
| 10 | One read-only tool works after reconnect | That second process's `mcp__aip__get_service_dependencies` call for `service:order-service` (same observation window) returned `outcome: PARTIAL` with 4 dependency claims (`unused-q` `NOT_OBSERVED_IN_WINDOW`, `legacypricingservice` `OBSERVED_ONLY`, `payment-service` `CONFIRMED`, `product-service` `CONFIRMED`) and `producer.build_revision = 6461db6d51ee29e9c973e62b005aa84d5d95c077` — again the exact candidate SHA. |

**Confirmation that the real client no longer reaches the former trigger path** (not, by itself,
direct execution of the exact original hanging request — see below): the passive capture shows every
one of the 4 client processes (including the two `claude mcp get`/`list` connectivity checks — the
exact commands that hung the pre-fix candidate) opens with the identical
`mcp-method: server/discover` / `mcp-protocol-version: 2026-07-28` probe found in the original
root-cause isolation below, `User-Agent: claude-code/2.1.270 (sdk-cli)` unchanged. `server/discover`
itself never hung, before or after the fix — the original root-cause isolation's own finding is that
`server/discover` always returned a plausible `200 OK`, and the actual hanging request was the
*follow-up* `mcp-method: subscriptions/listen` sent immediately after it. In this run, every one of
the 4 `server/discover` probes now returns instantly with a clean rejection instead (`HTTP 404`,
`{"jsonrpc": "2.0", "id": "server-discover-probe-1", "error": {"code": -32601, "message": "Method not
found", "data": "server/discover"}}`), and — critically — no client process in this capture ever sent
`subscriptions/listen` at all: the clean rejection of `server/discover` evidently causes the client to
skip that follow-up call entirely and fall through to its ordinary negotiated `initialize` (protocol
`2025-11-25`). This proves the real client's actual negotiation path no longer reaches the former
trigger request under real, unmodified client behavior; it does not itself exercise
`subscriptions/listen`. For direct proof that `subscriptions/listen` itself now returns `-32601`
without hanging (rather than inferring it from the client never sending it), see
`tests/integration/test_mcp_direct_marker_dos_regression.py::test_subscriptions_listen_cannot_hang_the_server`
(the exact real-world reproduction, run in a subprocess with an OS-enforced timeout) and the sanitized
`curl` reproduction in the Historical record's "Sanitized reproduction" section below, both added by
the ADR 0014 amendment. `/health` and the rest of the demo remained responsive throughout every
process in this run.

### Sanitization statement (spec §6.15)

The passive capture and `claude -p --output-format json` transcripts/session files contained no
authorization headers, bearer tokens, cookies, API keys, refresh tokens, account identifiers, email
addresses, personal user identifiers, raw system prompts, or unrelated conversation/traffic (this AIP
demo endpoint requires no credential at all). The client-identifying string
`User-Agent: claude-code/2.1.270 (sdk-cli)` is retained as legitimate client-version evidence, not a
personal identifier. The same statement applies to the Appendix A.2 UX observation's verbatim agent
answer recorded below: it contains only architecture-fact content returned by AIP's own tools, with no
headers, tokens, identifiers, or unrelated content of any kind. Raw `.pcap` capture files and session
transcript files were ephemeral, used only to produce the excerpts and summaries in this trace, and
were deleted (`rm`, and the corresponding `~/.claude/projects/.../*.jsonl` files) before this
qualification run's tuple closure.

### Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `9` — equal to `revision_before` (`R = 9`). This check was taken immediately after the two connectivity-check processes and the two `claude -p` processes covered by the protocol-qualification/reconnect evidence above (4 tool calls total: 3 in run 1, 1 in run 2) and **before** the separate Appendix A.2 UX run below. |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged (`aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`), matching the pre-client snapshot `S`. Same timing as `revision_after`: taken before the UX run. |

This tuple's own fence/fixture recheck covers the full protocol-qualification/reconnect evidence above
but **not** the separate Appendix A.2 UX run below, which was executed afterward in its own fresh
process (2 more tool calls: one `get_architecture_drift`, one `get_evidence` resolving all three
references in a single call) and was not independently re-fenced. As with the Codex CLI trace from
this same qualification pass, the release-level zero-write claim for that portion rests on spec
§6.12's explicit joint-support model (fence measurement + the automated zero-write test suite): the UX
run's two calls used only `get_architecture_drift`/`get_evidence`, both already proven zero-write for
every direct/negotiated routing path by
`tests/integration/test_mcp_i1_zero_write_completion_gate.py`, independent of which client issues the
call.

### Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh `claude -p` process/session, separate from the protocol-qualification runs above, and
after this tuple's own post-client revision-fence/fixture recheck (see note above).

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Where visible:**

| | |
|---|---|
| Model/provider | `claude-sonnet-5` (Anthropic) — Claude Code's configured default model for this session; not overridden |
| Agent mode | `claude -p` (non-interactive, `--output-format json`) |
| Tool approval mode | `--allowedTools` pre-authorizing the same three AIP tools; no approval prompt was requested or reached; `permission_denials: []` |

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

> ## Query
>
> `get_architecture_drift` for `service:order-service`, environment `demo`, window
> `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`.
>
> - Snapshot: `aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`
> - Observation context: `aip:observation-context:v1:725f25b7b4ac7a526c1a32ecc1e2da9d937b77bcfb2e7a5155d7f42543987ceb`
> - Tool outcome: **PARTIAL** — one of the two claims below carries an unresolved-identity limitation,
>   so AIP itself flags this result as incomplete, not just "two clean findings."
>
> All evidence below was resolved with `get_evidence` against that **same** snapshot ID (required
> field on that tool — it never floats to "current").
>
> ---
>
> ## Finding 1 — `order-service` → `queue:unused-q` (SENDS)
>
> **1. Qualification**: `NOT_OBSERVED_IN_WINDOW`, coverage `SUFFICIENT`.
> This means: a DECLARED architecture fact exists (order-service sends to `unused-q`), and AIP had
> sufficient observation coverage in the demo environment for this window to trust a negative result —
> but no OpenTelemetry evidence of this send actually firing turned up in that window. It is drift in
> the "declared but not seen" direction.
>
> **2. Evidence resolved (same snapshot)**:
> - `evidence:asyncapi:order-service` (`DECLARED`, source `examples/order-service/asyncapi.yaml`) —
>   supports `SENDS order-service → queue:unused-q`, `CARRIES queue:unused-q → message:UnusedMessage`,
>   `CONFORMS_TO message:UnusedMessage → schema:UnusedMessage`.
> - `resolution_evidence_refs` is empty — AIP had no evidence resolving a downstream consumer for
>   `unused-q`.
>
> **3. What AIP actually established**: the AsyncAPI spec declares this send edge, and no runtime
> evidence for it appeared in the given demo window. `destination_resolution` is
> `DIRECT_TARGET_FALLBACK`, and AIP explicitly logged why: *"queue:unused-q has no single evidenced
> consumer service; retained as the direct queue target rather than guessed"* (`UNRESOLVED_IDENTITY`
> limitation). So the object of this claim is the queue itself, not a resolved downstream service.
>
> **4. Not to infer**: AIP does not establish that order-service *stopped* sending to this queue, that
> the send code path is dead, or who (if anyone) consumes `unused-q`. Absence of observation in a
> 24-hour window is not evidence of removal, and AIP names no consumer — it explicitly declined to
> guess one.
>
> ---
>
> ## Finding 2 — `order-service` → `service:legacypricingservice` (CALLS)
>
> **1. Qualification**: `OBSERVED_ONLY`, coverage `null`.
> This is the opposite direction of drift: a runtime call was seen, but there is no DECLARED evidence
> (OpenAPI/manifest) backing this dependency at all. `coverage` is null because that field quantifies
> confidence in a negative/declared-side result, which doesn't apply here — there's no declared claim
> to measure coverage against.
>
> **2. Evidence resolved (same snapshot)**:
> - `evidence:otel:demo:2026-08-26:bfae54276215` (`OBSERVED`, OpenTelemetry, `first_seen`=`last_seen`=
>   `2026-08-26T12:00:00.044222Z`, `observation_count: 1`, `correlation_mode: CLIENT_SERVER`) —
>   supports `CALLS service:order-service → operation:service:legacypricingservice:GET:/pricing/{sku}`.
> - `resolution_evidence_refs`: `evidence:otel:demo:2026-08-26:29d4976aeaf9` (`OBSERVED`, same
>   bucket/timestamp) — supports `PROVIDES service:legacypricingservice →
>   operation:...GET:/pricing/{sku}`, which is what let AIP resolve the callee to a concrete service
>   (`destination_resolution: RESOLVED_SERVICE`) instead of leaving it as a bare operation.
>
> **3. What AIP actually established**: exactly one client-server correlated OTel observation, in the
> demo environment, within the requested window, of order-service calling `GET /pricing/{sku}` on
> LegacyPricingService — and no DECLARED source (OpenAPI/manifest) documents this dependency. Note
> `observation_count: 1`: this is a single observed call pair, not a sustained pattern.
>
> **4. Not to infer**: AIP does not establish *why* this call is undeclared (missing manifest entry
> vs. a new/undocumented integration vs. a manifest that's simply stale), how frequently this call
> happens outside this one bucket, or whether it represents a "real" production dependency versus a
> one-off/test invocation. A single observation in a 24-hour demo-environment window is what AIP has —
> nothing about typical volume, criticality, or intent should be assumed beyond that.

This is observational product evidence only, not a semantic release gate (spec §7.2); the outcome
above happens to be a strong one, but the UX observation's contract-complete recording — not that
quality — is what §7.2 requires.

### Disposition

- `QUALIFIED` against `RELEASE_CANDIDATE_SHA = 6461db6d51ee29e9c973e62b005aa84d5d95c077`.
- Same-snapshot, reconnect, and exact-tool-count requirements independently confirmed via passive
  capture, not inferred from the `claude -p` transcript alone. Zero-write is confirmed for the full
  protocol-qualification/reconnect evidence by direct revision-fence measurement, and for the separate
  Appendix A.2 UX run's two calls by the automated zero-write test suite.
- The passive capture directly confirms the exact `server/discover` request that historically preceded
  the hang (see Historical record below) is now cleanly rejected in every one of the 4 client
  processes captured here, including the two `claude mcp get`/`list` connectivity checks that hung the
  pre-fix candidate — and that the client no longer proceeds to `subscriptions/listen` afterward.

---

## Historical record: FAILED attempt against the invalidated candidate `71e2d8b954fa92430723fced302baa3666255397`

Preserved unedited below, per spec §6.5's requirement that an earlier valid-client failure is never
hidden by only reporting a later success.

### Tuple identity (as recorded at the time)

| Field | Value |
|---|---|
| Client family | Claude Code |
| Client product | Claude Code CLI |
| Client version | `2.1.270` |
| Extension/plugin | N/A — built in |
| OS | Linux 5.15.153.1-microsoft-standard-WSL2, x86_64 |
| Execution mode | WSL |
| Client location | Same host as AIP (localhost) |
| AIP location | Docker container, same host, published port `8000` |
| Network topology | Client (host, WSL) → `localhost:8000` (published port) → `architecture-intelligence` container |
| Configuration mechanism | `claude mcp add --transport http --scope local aip http://localhost:8000/mcp` (per `examples/mcp-clients/claude-code.md`, reverified against current `claude mcp add --help` output immediately before this run — syntax unchanged) |
| Transport | Streamable HTTP |
| Approval mode | Default (unmodified); no approval prompt was reached before the hang |
| Candidate SHA | `71e2d8b954fa92430723fced302baa3666255397` (**INVALIDATED** — see `v0.4.2-rc.1-candidate-preparation.md`) |
| Returned `producer.build_revision` | Not reached — the hang occurred before any AIP tool was called |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | `2026-07-28` (from the client's own `mcp-protocol-version` header on its `server/discover`/`subscriptions/listen` requests) |
| Session IDs issued / used / reuse | None observed |
| Qualification date | 2026-09-13 |

### Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
the (then-believed-good) candidate. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

### Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 1 | `TRANSPORT_FAILURE` | `claude mcp add ...` succeeded; `claude mcp list`'s own connectivity health-check hung the server indefinitely instead of completing |

This is a **valid client attempt** per §6.5 (the I2 fixture/server/network prerequisites were healthy
at the moment the client made its request) that fails the tuple with `TRANSPORT_FAILURE`
("prerequisites healthy enough to assess the client, but initialization, protocol exchange, or
reconnect failed") — not `INFRASTRUCTURE_FAILURE`, because the failure is not independent of the
request the client sent; it is a direct, deterministic consequence of that request.

### Root-cause isolation

Confirmed via direct, controlled reproduction (each step re-run against a freshly restarted, healthy
server) — capture method: passive `tcpdump` on the loopback/bridge path between the host and the
published container port (observational only; no header/body/method was inserted, rewritten, or
simulated, per spec §6.14), cross-checked against AIP's own uvicorn access log:

1. **The real trigger.** `claude mcp list`'s health probe sent, in order: `mcp-method: server/discover`
   (protocol `2026-07-28`) → `200 OK`, a plausible-looking response; then
   `mcp-method: subscriptions/listen` (same protocol era) → no response ever sent. Docker's own
   healthcheck (`GET /health` from inside the container) then failed every 30s from that point on
   until the container was restarted; CPU pegged at ~100% the whole time.
2. **Isolated from the client entirely.** A minimal `curl` — zero Claude Code involvement — replaying
   the exact captured `subscriptions/listen` request against a freshly restarted, healthy server
   reproduces the identical hang. This is an AIP-side defect, not a Claude Code bug or a local
   environment flake.
3. **Not "any unrecognized method hangs."** A bogus method name (`totally/bogus/method`) with the same
   headers returns a clean, instant `-32601 Method not found`.
4. **Not "any negotiated `subscriptions/listen`."** The same method sent as genuine negotiated
   traffic (protocol `2025-11-25`, no `mcp-method` header) also returns a clean, instant
   `-32601 Method not found`.
5. **Not "protocol era `2026-07-28` alone."** That header alone, without an `mcp-method` header, is
   already cleanly rejected by AIP's own guard (`400`, "the direct protocol era cannot be used for a
   negotiated follow-up request").
6. **Isolated to the exact combination**: an `mcp-method` header present (which `app/mcp/guard.py`
   treated as an "AIP-specific direct-envelope marker") **and** a method name — `subscriptions/listen`
   — that the pinned MCP SDK recognizes as a real, legitimate method under protocol era `2026-07-28`,
   for a long-lived server-notification subscription AIP's stateless deployment never services. The
   guard forwarded it unmodified to the mounted SDK app on the assumption that "carries a direct
   marker" implied "safe to dispatch"; the SDK's own handling of that method then hangs.
7. **Not preemptable by an application-level timeout.** Wrapping the equivalent request in
   `asyncio.wait_for(..., timeout=5)` inside a test does not save it — the offending code does not
   yield control back to the event loop, so cancellation never gets a chance to run. The only safe fix
   is to never reach that code path at all.

### Sanitized reproduction

Minimal, complete, reproducible with `curl` alone:

```bash
curl http://localhost:8000/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -H 'mcp-method: subscriptions/listen' \
  -H 'mcp-protocol-version: 2026-07-28' \
  -d '{
        "jsonrpc": "2.0",
        "id": "listen:0",
        "method": "subscriptions/listen",
        "params": {
          "_meta": {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientInfo": {"name": "repro-client", "version": "0.0.0"},
            "io.modelcontextprotocol/clientCapabilities": {"roots": {"listChanged": true}, "elicitation": {}}
          },
          "notifications": {"toolsListChanged": true, "promptsListChanged": true, "resourcesListChanged": true}
        }
      }'
```

Before the fix: hangs indefinitely; the server becomes unresponsive to every other client, including
its own `/health` check, until the container is restarted. After the fix: returns instantly,
`HTTP 404`, `{"jsonrpc":"2.0","id":"listen:0","error":{"code":-32601,"message":"Method not found","data":"subscriptions/listen"}}`.

### Sanitization statement (spec §6.15)

The passive capture contained no authorization headers, bearer tokens, cookies, API keys, refresh
tokens, account identifiers, email addresses, personal user identifiers, raw system prompts, or
unrelated conversation/traffic — verified by direct inspection before any excerpt was used here (this
AIP demo endpoint requires no credential at all). The client-identifying string
`User-Agent: claude-code/2.1.270 (sdk-cli)` is retained as legitimate client-version evidence, not a
personal identifier. Raw `.pcap` capture files were ephemeral, used only for this investigation, and
were not retained beyond it.

### Post-client state (spec §6.12/§6.15)

| Field | Value |
|---|---|
| `revision_after` | `NOT_CAPTURED` — the server was completely unresponsive (hung, ~100% CPU) at the moment of failure; by the time it was restarted and queryable again, this attempt's window had closed, so no value was read for *this specific tuple attempt*. Not to be confused with `R = 9` recorded separately for a later, independent re-verification pass. |
| Fixture-check result | `NOT_EXECUTED` for the same reason — the checker could not be run against an unresponsive server, and no re-run before restart would have been a result *for this attempt*. |

These fields are recorded explicitly as unavailable, not treated as inapplicable: spec §6.15 requires
every committed trace artifact to record revision-before/after and the fixture-check result
regardless of outcome, and the governing spec defines no blanket exemption for a `TRANSPORT_FAILURE`
result. `revision_before = 9` (recorded above, spec §6.3, before the client was configured) is the
only revision-fence value this attempt actually captured.

The environment was restored to a clean, healthy state (container restarted, fixture torn down)
before proceeding to root-cause investigation and the fix.

### Disposition (as recorded at the time)

- Fix landed: `app/mcp/guard.py`'s direct-marked dispatch is now a closed allowlist
  (`tools/list`, `tools/call`); see ADR 0014's "Amendment" section and
  `docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md` §10.1.
- This candidate (`71e2d8b954fa92430723fced302baa3666255397`) is **INVALIDATED**.
- Claude Code's tuple requires a fresh qualification attempt against the new, post-fix
  `RELEASE_CANDIDATE_SHA`, per spec §4.4 and §6.5 ("A client/control failure on that one valid
  attempt fails the tuple until the underlying defect or configuration is corrected and qualification
  is restarted").
- Codex CLI's separately completed, fully successful qualification attempt against this same
  invalidated candidate is unaffected in substance (it never touched the defective code path), but
  per spec §4.4 must still be reconfirmed against the new candidate before being recorded as
  `QUALIFIED` for release.

Both requirements above are satisfied: see the "Requalification against `RELEASE_CANDIDATE_SHA =
6461db6d51ee29e9c973e62b005aa84d5d95c077`" section at the top of this file (Claude Code) and
`docs/release-validation/v0.4.2-client-traces/codex-cli.md` (Codex CLI).
