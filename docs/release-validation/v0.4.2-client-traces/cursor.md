# Cursor — Actual-Client Trace (I3.4)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **UNVERIFIED** (procedure gap — not a semantic finding)

Executed by the repository owner on their own machine (Cursor has no CLI/headless automation path;
per the I3 plan, Cursor and VS Code qualification is operator-run, not driven by this agent). Evidence
tier for this trace is **client UI evidence** (spec §6.13's own list of acceptable sources includes
this explicitly) — chat transcripts and command output relayed by the operator in real time, not a
passive network capture or session-file inspection as was possible for Codex CLI/Claude Code, which
this agent drove directly.

**This run does not satisfy the mandatory §6.2/§6.3/§6.12 baseline-and-fence contract and therefore
cannot be recorded as `QUALIFIED`, per PR #149 review.** `check_fixture_state.py`/`read_revision_fence.py`
were not executed *before* Cursor was configured or interacted with AIP, so there is no tuple-local
`revision_before`/pre-client fixture-state proof — only a post-run reading, taken after Cursor had
already made every call in this trace. §6.12's zero-write proof is specifically about detecting a
write *this run* might have made; a baseline borrowed from other clean builds' post-seed readings
cannot stand in for that, however consistent those other readings have been. This gap cannot be
repaired retrospectively in prose. Everything else below is retained as an accurate record of what was
observed, and the semantic protocol behavior itself was correct — but the tuple as a whole requires a
clean re-run, starting from an unconfigured candidate worktree, with both helpers executed and recorded
*before* any client configuration or interaction. Separately, and independently of this gap, the
tested candidate (`6461db6d51ee29e9c973e62b005aa84d5d95c077`) has itself been found to have an
unrelated defect during VS Code qualification, recorded in currently open
[PR #150](https://github.com/michaelegner/architecture-intelligence-platform/pull/150) (not yet
merged as of this trace's own commit) — that PR's branch, not this one, carries
`docs/release-validation/v0.4.2-rc.2-candidate-preparation.md`'s invalidation notice. Once #150 merges
and a new candidate is frozen, the required clean re-run described above will happen against that new
candidate rather than `6461db6d...` directly.

## Tuple identity

| Field | Value |
|---|---|
| Client family | Cursor |
| Client product | Cursor |
| Client version | `3.20.17` |
| Extension/plugin | N/A — built in |
| OS | Windows (host) + WSL2 (Linux distro), exact Windows build/CPU architecture not captured |
| Execution mode | WSL — Cursor (Windows desktop app) connected to the WSL2 distro via its Remote-WSL-equivalent, working directory `/tmp/aip-i34` inside WSL |
| Client location | Windows host process, remote-connected into the same WSL2 VM as AIP |
| AIP location | Docker container inside WSL2, published port `8000` |
| Network topology | Cursor (Windows, WSL-remote-connected) → `localhost:8000` (WSL2 published port, reachable from both the WSL guest and the Windows host) → `architecture-intelligence` container |
| Configuration mechanism | `.cursor/mcp.json` in the worktree root: `{"mcpServers": {"aip": {"url": "http://localhost:8000/mcp"}}}`, per `examples/mcp-clients/cursor.md` |
| Transport | Streamable HTTP (`url` field, no `type`/`command`, matching Cursor's remote-HTTP server shape) |
| Candidate SHA | `6461db6d51ee29e9c973e62b005aa84d5d95c077` |
| Returned `producer.build_revision` | `6461db6d51ee29e9c973e62b005aa84d5d95c077` — exact match, confirmed by asking the agent to quote it directly from the `get_architecture_drift` response it had just used (not inferred from the checkout or image) |
| Pinned MCP SDK version (AIP side) | `mcp==2.2.0` |
| Observed initialization/protocol version | Not independently captured (no network capture available in this environment); tool discovery and correct three-tool behavior were confirmed via Cursor's own MCP settings panel and via every tool call succeeding |
| Session IDs issued / used / reuse | Not independently captured for the same reason; AIP's negotiated mode issues no session IDs in any of the automated/passive-capture evidence gathered for the other three client families, and nothing in this run's behavior (three independent chat contexts all working statelessly) is inconsistent with that |
| Qualification date | 2026-09-13 |

## Approval behavior (spec §6.7)

| Field | Value |
|---|---|
| Approval mode | Default Cursor Agent-mode tool execution |
| Approval requested | No — operator confirmed all tool calls (drift qualification run, reconnect check, UX run) executed automatically, with no approve/allow prompt shown |
| Manual approval required | No |
| Persistent allow enabled | Not applicable / not distinguishable from "no prompt needed by default" in this evidence tier — the operator did not need to enable or interact with any allow-list setting to get this automatic behavior |

## Configuration re-verification (spec §6.4)

| | |
|---|---|
| Official source | <https://cursor.com/docs/mcp> |
| Verification date | 2026-09-13 (this run) |
| Result | PASS — confirmed by fetching the raw page source directly (not a summarization tool, per the lesson from this same qualification pass's Codex CLI trace) and finding the exact `{"mcpServers": {"server-name": {"url": "http://localhost:3000/mcp", "headers": {...}}}}` shape and the `.cursor/mcp.json` file path, both matching `examples/mcp-clients/cursor.md` exactly (AIP's config omits `headers` since no auth is required). No finding. |

## Pre-client state (spec §6.2/§6.3) — **NOT CAPTURED, blocking**

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
`6461db6d51ee29e9c973e62b005aa84d5d95c077`, run by the operator from a clean `git worktree --detach`
at that exact SHA. The script's own completion output ("AIP demo is ready", MCP endpoint
`http://localhost:8000/mcp`) and a `curl /health` check were confirmed before any client was
configured.

**`check_fixture_state.py`/`read_revision_fence.py` were not run before Cursor was configured or
before any client interaction.** Per PR #149 review, this is a blocking gap, not a cosmetic one:
§6.2/§6.3 require `fixture = COMPLETE`, `snapshot_id = S`, and `revision_before = R` captured for
*this* tuple before the client touches AIP, and §6.12's zero-write proof is specifically a tuple-local
`R' = R` comparison — it cannot be satisfied by a baseline borrowed from a different execution, however
consistent that other execution's own readings have been. See Result above and Post-client state below.

## Attempt record (spec §6.5/§6.6)

| Cycle | Attempt | Classification | Outcome |
|---|---|---|---|
| 1 | 1 | `CLIENT_CONTROL_FAILURE` (PR #149 review reclassification) | The operator's first message to Cursor was their own paraphrase of the required task rather than the fixed Appendix A.1 prompt verbatim — the qualification control failed to issue the required fixed prompt. AIP/demo/network/fixture prerequisites were healthy at that moment (Cursor connected and ran all three tools correctly against the request it was actually given, including `get_service_dependencies`, which the fixed prompt does not request), so this is a genuine valid client attempt, not infrastructure invalidation, and not a free-standing "methodology discard" category the spec does not define. §6.8's "the requested architecture operation MUST NOT change" is exactly the requirement this attempt violated. Per §6.5, this **fails cycle 1's tuple** outright, analogous to the documented Codex CLI restart after its own control/configuration failure. |
| 2 | 1 | — | Configuration corrected — a fresh chat, with the actual fixed Appendix A.1 prompt pasted verbatim. Full success: called `get_architecture_drift`, then `get_evidence` using exactly the `evidence_refs`/`snapshot_id` it returned, and reported the AIP qualifications exactly. Notably precise: the drift response for the `LegacyPricingService` claim also carried a `resolution_evidence_refs` entry not part of that claim's own `evidence_refs`, and the agent correctly did **not** pass it to `get_evidence`, matching the prompt's "exactly the evidence_refs" instruction more strictly than either of the other two client traces' UX runs did. |

Recorded per cycle, not aggregated away: **cycle 1 consumed one valid attempt and failed**
(`CLIENT_CONTROL_FAILURE`); **after the recorded correction, cycle 2 consumed one valid attempt and
produced the semantic result above.** Two valid client attempts total across both cycles, each
individually within the LLM-mediated per-cycle budget of 2 (spec §6.5). This attempt-accounting
correction stands regardless of the separate, blocking pre-client-baseline gap above — the tuple's
final result is `UNVERIFIED` because of the missing baseline, not because of this cycle-1 failure,
which is itself now correctly recorded rather than hidden.

## Required successful protocol workflow (spec §6.8)

Evidence source for this section is the operator's relayed chat transcripts (client UI evidence, spec
§6.13) rather than a passive network capture.

| # | Requirement | Evidence |
|---|---|---|
| 1 | Initialization/negotiation | Cursor's MCP settings panel showed `aip` as connected before the qualification run began. |
| 2 | Tool discovery | Same panel, listing the server's tools. |
| 3 | Exactly three AIP tools discovered | Confirmed via the settings panel: `get_architecture_drift`, `get_evidence`, `get_service_dependencies` — no others (operator was specifically asked to check this during setup). |
| 4 | `get_architecture_drift` | Cycle 2's response: drift called for `service:order-service`, `demo`, `2026-08-26T00:00:00Z`–`2026-08-27T00:00:00Z`. |
| 5 | Deterministic structured drift result | `queue:unused-q` → `NOT_OBSERVED_IN_WINDOW` (coverage `SUFFICIENT`, `DIRECT_TARGET_FALLBACK`, `UNRESOLVED_IDENTITY` limitation) and `service:legacypricingservice` (via `GET /pricing/{sku}`) → `OBSERVED_ONLY` — the exact spec §6.9 expected result. |
| 6 | `get_evidence` using returned `evidence_refs` | `evidence:asyncapi:order-service` (for the `unused-q` claim) and `evidence:otel:demo:2026-08-26:bfae54276215` (for the `LegacyPricingService` claim), both taken verbatim from the drift response's per-claim `evidence_refs` — and, as noted above, the claim's separate `resolution_evidence_refs` (`evidence:otel:demo:2026-08-26:29d4976aeaf9`) was correctly *not* passed, since it wasn't part of `evidence_refs`. Both `get_evidence` calls `ANSWERED`, `missing_evidence_refs: []`. |
| 7 | Same snapshot used | All calls carry `snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`. |
| 8 | Disconnect/stop | Operator reloaded the Cursor window ("Reload Window"), closing the prior chat's MCP session. |
| 9 | Reconnect/reinitialize | A fresh chat, after the reload, successfully discovered and called AIP's tools again from scratch. |
| 10 | One read-only tool works after reconnect | `get_service_dependencies` for `service:order-service` (same window) returned `outcome: PARTIAL` with the same 4 dependency claims as the other two clients' equivalent calls (`unused-q` `NOT_OBSERVED_IN_WINDOW`, `legacypricingservice` `OBSERVED_ONLY`, `payment-service` `CONFIRMED`, `product-service` `CONFIRMED`), same snapshot. |

## Sanitization statement (spec §6.15)

All evidence in this trace is text relayed directly by the repository owner from their own Cursor
session, describing only AIP architecture-fact content (service/queue/evidence identifiers, tool
qualifications) — no authorization headers, tokens, cookies, account identifiers, email addresses,
personal identifiers, raw system prompts, or unrelated content of any kind appeared in any of it. AIP's
local demo endpoint requires no credential, so no header/token redaction was needed. No raw capture
file exists for this trace (none was produced in this evidence tier).

## Post-client state (spec §6.12/§6.15) — **incomplete: no tuple-local baseline to compare against**

| Field | Value |
|---|---|
| `revision_after` | `9` — measured directly via `read_revision_fence.py --json` after all three chat interactions (drift qualification, reconnect check, UX run) had completed. |
| Fixture-check result | `COMPLETE`, `mismatches: []`, `actual_snapshot_id` unchanged (`aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`), matching every snapshot ID quoted throughout the run. |

`revision_before` was not independently measured for this specific tuple (see Pre-client state above),
and per PR #149 review this is a **blocking** gap, not a merely-preferred one: §6.12's zero-write proof
is a tuple-local `R' = R` comparison whose entire purpose is to detect a write *this run* might have
made. A baseline value borrowed from other clean builds' post-seed readings — however consistently
those other readings have come out at `9` elsewhere in this I3 pass — is not the same evidence and
cannot be substituted for it. `revision_after = 9` and the clean fixture classification above remain
accurate observations, but they do not by themselves prove this specific run wrote nothing, and this
record no longer claims otherwise.

## Mandatory separate UX observation (spec §7.2, Appendix A.2)

Run in a fresh Cursor chat, separate from the protocol-qualification and reconnect runs above.

**Prompt used:** the fixed Appendix A.2 prompt, verbatim.

**Where visible:**

| | |
|---|---|
| Model/provider | Not captured — Cursor's chat UI in this run did not surface which underlying model served the request, and the operator was not asked to check Cursor's model-selector setting retroactively |
| Agent mode | Cursor's default Agent-mode chat |
| Tool approval mode | Automatic — no approval prompt requested or reached (same as the protocol-qualification run) |

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

> AIP returned two drift claims for service:order-service in demo, window
> 2026-08-26T00:00:00Z–2026-08-27T00:00:00Z. Tool outcome is PARTIAL. Snapshot:
> aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8
>
> Evidence was resolved with get_evidence on that same snapshot; all three refs were found.
>
> A structured review is in OrderService drift — a canvas you can open beside the chat. I used that so
> the claims, qualifications, and resolved evidence stay bound to the snapshot instead of living only
> in this message.
>
> **Finding 1 — declared send to queue:unused-q**
> Claim: aip:claim:v1:ca0dd73ba391552edd6d2cc06cddd919a8af97f362cdb47392e78325219fd612
>
> Qualification: NOT_OBSERVED_IN_WINDOW with coverage SUFFICIENT. Predicate DIRECT_DEPENDENCY.
> Delivery is ASYNC_MESSAGE / SENDS via queue:unused-q. Destination resolution is
> DIRECT_TARGET_FALLBACK: the object is the queue, not a consumer service.
>
> Evidence (same snapshot): evidence:asyncapi:order-service — type DECLARED, source ASYNCAPI, locator
> examples/order-service/asyncapi.yaml, no observation payload; among its supports rows, the one this
> claim uses is SENDS service:order-service → queue:unused-q; resolution_evidence_refs is empty.
>
> Limitation attached to this claim: UNRESOLVED_IDENTITY — AIP states queue:unused-q has no single
> evidenced consumer service and was kept as the direct queue target rather than guessed. That is why
> the outcome is PARTIAL.
>
> What AIP established: OrderService declares a send to unused-q; in this window, with coverage marked
> sufficient, that dependency was not observed; AIP did not resolve a consumer.
>
> Not established: why nothing was observed; whether anything was sent outside this window; a consumer
> of unused-q; anything about other relations on the same AsyncAPI record (payment-q, CARRIES,
> CONFORMS_TO) — those are on the evidence record, not this drift claim.
>
> **Finding 2 — observed call to LegacyPricingService**
> Claim: aip:claim:v1:8c43c7b5ba7783da9b188afd0e28a72d0570d3a48a9772c5911ce8469e89bbd0
>
> Qualification: OBSERVED_ONLY. Coverage is null. Predicate DIRECT_DEPENDENCY. Delivery is SYNC_HTTP /
> CALLS via operation:service:legacypricingservice:GET:/pricing/{sku}. Destination resolution is
> RESOLVED_SERVICE; object is service:legacypricingservice.
>
> Evidence (same snapshot): evidence:otel:demo:2026-08-26:bfae54276215 (claim evidence) — OBSERVED /
> OPENTELEMETRY; demo; bucket matches the window; first/last seen 2026-08-26T12:00:00.044222Z; count
> 1; CLIENT_SERVER; supports CALLS service:order-service → that operation. evidence:otel:demo:
> 2026-08-26:29d4976aeaf9 (resolution evidence) — same observation fields; supports PROVIDES
> service:legacypricingservice → that operation.
>
> What AIP established: in this demo window, OpenTelemetry observed OrderService calling
> GET /pricing/{sku}, and separately observed LegacyPricingService providing that operation, which is
> how the destination was resolved to service:legacypricingservice. No declared evidence is attached
> to this claim.
>
> Not established: a declared CALLS (or declared PROVIDES) for this edge; intent, ownership, or
> policy; more than one observation; service version (null on both OTEL records).
>
> Nothing else was added beyond get_architecture_drift and get_evidence on this snapshot.

This is observational product evidence only, not a semantic release gate (spec §7.2). Worth noting as
UX-quality product evidence (not a release gate itself): Cursor rendered the structured claim/evidence
data in a side "canvas" panel alongside the chat response, a client-specific presentation choice not
observed in either of the other two client families' UX runs.

## Disposition

- `UNVERIFIED` against `RELEASE_CANDIDATE_SHA = 6461db6d51ee29e9c973e62b005aa84d5d95c077` (PR #149
  review) — not `QUALIFIED`, because the mandatory tuple-local pre-client fixture/revision baseline
  (§6.2/§6.3) was never captured, which means §6.12's zero-write proof cannot be completed for this
  specific run. The semantic protocol behavior observed (correct deterministic drift/evidence result,
  correct reconnect, correct `producer.build_revision`) is accurate and retained, but is not sufficient
  by itself for `QUALIFIED` under the frozen procedure.
- Cycle 1's non-fixed-prompt paraphrase is now correctly classified as a valid client attempt that
  failed with `CLIENT_CONTROL_FAILURE` (the qualification control failed to issue the required fixed
  prompt) rather than left in an undefined "discarded methodology" bucket — recorded and counted, not
  hidden, per spec §6.5/§6.6/§6.8.
- Evidence tier is client UI evidence (spec §6.13), not passive network capture or session-file
  inspection — the gaps this implies beyond the blocking baseline gap above (initialization/
  protocol-version header, session-ID behavior, UX-run model/provider) remain recorded explicitly.
- **Required remediation:** re-run this tuple from a clean, unconfigured candidate worktree —
  execute and record `check_fixture_state.py`/`read_revision_fence.py` *before* any client
  configuration or interaction, then the fixed Appendix A.1 prompt verbatim (cycle 1, this time run
  correctly the first time), reconnect, the final helpers, and the separate Appendix A.2 UX run, all in
  that order. This did not happen against `6461db6d51ee29e9c973e62b005aa84d5d95c077` because that
  candidate has separately been found to have an unrelated VS Code transport defect, recorded in
  currently open [PR #150](https://github.com/michaelegner/architecture-intelligence-platform/pull/150)
  (not yet merged as of this trace's own commit; that PR's branch carries the actual invalidation
  notice, not this one) — once #150 merges and a new candidate is frozen, the required clean re-run
  will happen against that new candidate instead, applying both corrections from the start.
