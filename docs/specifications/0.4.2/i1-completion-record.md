# I1 Completion Record — v0.4.2 Dual-Mode MCP Transport

**This record is retrospective.** I1 (`docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md`,
merged to `main` as `2b6f865` via PR #135) did not originally require a candidate-bound completion
record — only a narrative "Implementation record" section in
[ADR 0014](../../adr/0014-negotiated-mcp-client-interoperability.md). I3's entry gate (spec
`i3-client-qualification-and-release-preparation.md` §3.1) requires one, so this record is written
now, after I1 and I2 are both complete, satisfying that gate.

## Run identity

- **I1 (Dual-Mode MCP Transport):** merged to `main` as `2b6f865` (PR #135, predates I2 entirely).
- **Candidate binding:** `RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0`, frozen by
  I3.2's second re-freeze (`docs/release-validation/v0.4.2-rc.3-candidate-preparation.md`), superseding
  the `6461db6d51ee29e9c973e62b005aa84d5d95c077` binding. This is the second genuine behavior-change
  rebind for this record (the first being `71e2d8b` → `6461db6d`, for the direct-marked-method
  allowlist fix): I3.4's actual-client qualification against `6461db6d` found that
  `app/mcp/guard.py`'s negotiated-mode branch hard-rejected any markerless follow-up request missing
  an `MCP-Protocol-Version` header — stricter than both the pinned SDK's own already-implemented
  missing-header fallback and the MCP specification's own server-side backward-compatibility
  allowance for exactly this case (the client-side rule is a separate MUST that a real client, VS
  Code's GitHub Copilot Chat MCP client, does not fully honor on `notifications/initialized`; AIP's
  job per the spec is to tolerate that gracefully, not reject it). `6461db6d` is INVALIDATED for this
  reason (see `docs/release-validation/v0.4.2-rc.2-candidate-preparation.md`'s own invalidation
  notice). The fix — forwarding a markerless follow-up with a missing header to the pinned SDK, while
  still rejecting one whose header is *present* and explicitly names the direct/single-exchange
  `2026-07-28` era — is recorded in
  [ADR 0014's second Amendment section](../../adr/0014-negotiated-mcp-client-interoperability.md) and
  in `docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md` §11/§11.1/§12/§28. This record's I1
  §3.1 table and exit statement below are updated accordingly, and the regression suite was re-run in
  full at `50862a352626ea38d2fbb36f2ff0ecfc667266d0` — a genuine re-verification, not a citation-only
  rebind.

## Regression suite (full local run at `RELEASE_CANDIDATE_SHA`)

| Suite | Result |
|---|---|
| `uv run ruff check .` | clean |
| `uv run ruff format --check .` | clean |
| `uv run pytest tests/unit` | 1001 passed |
| `uv run pytest tests/integration` | 288 passed |

1001/288 — identical counts to the prior `6461db6d` binding. PR #150's fix consolidated two unit-level
regression helpers into one dedicated scenario test
(`_check_vscode_full_sequence_without_protocol_header_is_accepted`), still called from inside the
single existing `test_mcp_protocol_and_discovery` test item, so this adds **zero** collected unit-test
items — same net effect as the direct-marked-method allowlist fix's own helper additions before it.
No integration test file was added or removed by this fix, so the 288 count also carries over
unchanged; the underlying assertions are strictly stronger (exact `initialize` →
`notifications/initialized` → `tools/list` sequence performed by one test, exact `202`/empty-body
notification response asserted rather than "200 or 202").

## I1 §3.1 required items

| Item | Evidence |
|---|---|
| Direct mode (unchanged v0.4.0 envelope) | `tests/unit/test_mcp_discovery.py::test_mcp_protocol_and_discovery` — all pre-existing `_check_*` helpers exercising the direct envelope |
| Direct-marked method allowlist (I3.3 correction, spec §10.1) | `tests/unit/test_mcp_discovery.py`'s `_check_another_unimplemented_direct_marked_method_is_also_rejected` (proves the fix is a general allowlist, not a `subscriptions/listen`-specific denylist entry — the other real Claude Code method observed, `server/discover`, is rejected the same way), `_check_header_body_mismatch_takes_priority_over_unimplemented_method`, `_check_server_stays_responsive_after_rejecting_an_unimplemented_direct_method`; `tests/integration/test_mcp_direct_marker_dos_regression.py::test_subscriptions_listen_cannot_hang_the_server` (the exact `subscriptions/listen` reproduction, run in a genuinely separate OS process with an OS-enforced socket timeout — an in-process `asyncio.wait_for` check cannot bound this hang, since the offending SDK code never yields to the event loop) |
| Negotiated mode | `tests/unit/test_mcp_discovery.py`'s `_check_markerless_initialize_reaches_negotiated_sdk_path`, `_check_negotiated_tools_call_shares_the_direct_tool_implementation` |
| Negotiated missing-header fallback (I3.4 correction, spec §11) | `tests/unit/test_mcp_discovery.py`'s `_check_vscode_full_sequence_without_protocol_header_is_accepted` (the directly-observed real-world `initialize` → headerless `notifications/initialized` reproduction, plus the broader `tools/list` fallback contract, in one dedicated scenario — exact `202`/empty-body notification response asserted), `_check_markerless_tools_list_without_header_falls_back_to_sdk`, `_check_markerless_tools_call_without_header_falls_back_to_sdk`, `_check_session_id_header_alone_is_not_a_direct_marker` (a session id alone, still no version header, is delegated the same way); `_check_direct_era_header_without_marker_is_rejected` confirms a *present* direct-era header without a marker is still rejected, unaffected by this fix |
| Malformed-body precedence | `tests/unit/test_mcp_discovery.py`'s `_check_malformed_json_without_direct_header_reaches_sdk_parse_handler` (owned by the SDK's parser when no direct header is present) and `_check_malformed_json_with_direct_header_is_owned_by_direct_path` (stays on the direct path when `mcp-method` is present) |
| Unsupported HTTP methods (405 contract) | `tests/unit/test_mcp_discovery.py`'s `_check_get_is_rejected_with_405_before_sdk_invocation`, `_check_delete_is_rejected_with_405_before_sdk_invocation`, `_check_head_is_rejected_with_405_and_empty_body`, `_check_other_non_post_methods_are_rejected_with_405` (PUT/PATCH/OPTIONS) |
| Origin/Host enforcement | `tests/unit/test_mcp_discovery.py::_check_disallowed_origin_is_rejected`; `tests/integration/test_mcp_negotiated_transport.py::test_negotiated_origin_and_host_security_matches_direct_mode` (proves the negotiated path introduces no bypass) |
| Cross-mode semantic equivalence | `tests/integration/test_mcp_negotiated_transport.py::test_direct_and_negotiated_structured_content_are_semantically_equivalent`, `::test_cross_mode_snapshot_interoperability_both_directions` (both directions), `::test_mandatory_negotiated_flow_against_real_data` (full initialize → tools/list → drift → evidence → disconnect → reconnect flow against real graph data) |
| Conditional-session result | **`NOT_APPLICABLE`** — `tests/unit/test_mcp_discovery.py::_check_negotiated_mode_issues_no_session_id` confirms no session IDs are issued in either mode; the candidate issues no session IDs and no I2 client tuple requires stateful sessions (I3 spec §3.3's `NOT_APPLICABLE` condition) |
| Automated zero-write result | `tests/integration/test_mcp_i1_zero_write_completion_gate.py::test_zero_graph_writes_across_every_i1_routing_path` — see below |
| I1 blockers | `0` |

### Closing a real gap: the automated zero-write result

Before this record, zero-write evidence existed but was split across three per-tool,
**direct-mode-only** files — `test_mcp_service_dependencies_equivalence.py`,
`test_mcp_architecture_drift_equivalence.py`, `test_mcp_evidence_equivalence.py` — each proving one
tool leaves `(:AipInternalState).revision` unchanged for a successful and a refused call. None of
them, nor any other file, proved "zero graph writes across *all* I1 routing paths" (direct **and**
negotiated, all three tools, including malformed/rejected requests) in one place, which is exactly
what I3 spec §3.1/§3.3/§8.3 require as I1 completion evidence.

New file `tests/integration/test_mcp_i1_zero_write_completion_gate.py` closes this: one test brackets
a single `read_revision` before/after a sequence covering direct-mode success (all three tools) and
rejection (malformed body, unsupported HTTP method `GET`), then negotiated-mode success (all three
tools, via a real `initialize` handshake) and rejection (malformed body, unsupported protocol
version) — asserting the fence never advanced across the entire run. It complements, rather than
duplicates, the three existing files' broader semantic-equivalence assertions.

## Scope preservation

- `ArchitectureAnswer<T>` schema family: unchanged, `schema_version` still `"0.4"`.
- Exactly three read-only MCP tools: unchanged.
- Public MCP path `/mcp`: unchanged, `POST`-only in this stateless release.
- Canonical Model / graph schema: unchanged — I1 is a transport-layer increment only.

## I1 exit statement

> GO — At `50862a352626ea38d2fbb36f2ff0ecfc667266d0` (`RELEASE_CANDIDATE_SHA`, re-frozen a second time
> by I3.2 after `6461db6d51ee29e9c973e62b005aa84d5d95c077`'s invalidation, which itself superseded
> `71e2d8b954fa92430723fced302baa3666255397`), AIP's direct (`2026-07-28`) and negotiated MCP
> transport modes remain semantically equivalent: identical `ArchitectureAnswer` results for
> equivalent requests, identical snapshot/evidence continuity in both cross-mode directions, identical
> Origin/Host protection, and identical non-POST rejection behavior. Neither mode issues a session
> identifier (`NOT_APPLICABLE` for conditional-session qualification). Zero graph writes occur across
> every I1 routing path — direct and negotiated, success and rejection, for all three tools — proven
> in one consolidated test rather than only per-tool. A direct-marked request naming a method outside
> the closed allowlist AIP has ever actually implemented for direct mode (`tools/list`, `tools/call`)
> is rejected with a clean `METHOD_NOT_FOUND` (-32601) rather than blindly forwarded to the mounted
> SDK app — closing the single-request denial-of-service found during I3.3 actual-client
> qualification (a real Claude Code client's legitimate `subscriptions/listen` traffic hung the server
> indefinitely under the pre-fix candidate). A markerless negotiated follow-up with no
> `MCP-Protocol-Version` header at all is now forwarded to the pinned SDK's own graceful fallback
> rather than hard-rejected — closing the connection failure found during I3.4 actual-client
> qualification (VS Code's real GitHub Copilot Chat MCP client, which omits this header on
> `notifications/initialized`, could not connect to AIP at all under the pre-fix candidate); a
> markerless follow-up whose header is present and explicitly names the direct/single-exchange era
> remains rejected, unaffected. I1 blockers = 0.
