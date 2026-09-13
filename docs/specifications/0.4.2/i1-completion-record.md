# I1 Completion Record — v0.4.2 Dual-Mode MCP Transport

**This record is retrospective.** I1 (`docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md`,
merged to `main` as `2b6f865` via PR #135) did not originally require a candidate-bound completion
record — only a narrative "Implementation record" section in
[ADR 0014](../../adr/0014-negotiated-mcp-client-interoperability.md). I3's entry gate (spec
`i3-client-qualification-and-release-preparation.md` §3.1) requires one, so this record is written
now, after I1 and I2 are both complete, satisfying that gate.

## Run identity

- **I1 (Dual-Mode MCP Transport):** merged to `main` as `2b6f865` (PR #135, predates I2 entirely).
- **Candidate binding:** `RELEASE_CANDIDATE_SHA = 6461db6d51ee29e9c973e62b005aa84d5d95c077`, frozen by
  I3.2's re-freeze (`docs/release-validation/v0.4.2-rc.2-candidate-preparation.md`), superseding the
  original `71e2d8b954fa92430723fced302baa3666255397` binding. Unlike the earlier rebind from
  `279c0ae` to `71e2d8b` (a pure citation update over an unmodified I1 suite), **this rebind follows a
  real I1 behavior change**: I3.3's actual-client qualification against `71e2d8b` found that
  `app/mcp/guard.py` forwarded any direct-marked request naming a method outside `{tools/list,
  tools/call}` straight to the mounted SDK app, and the SDK's own handling of at least one such
  method (`subscriptions/listen`, sent by a real Claude Code client) hangs the process indefinitely —
  a single-request denial-of-service reachable by any client. `71e2d8b` is INVALIDATED for this reason
  (see `docs/release-validation/v0.4.2-rc.1-candidate-preparation.md`'s own invalidation notice). The
  fix — closing the routing boundary to a general allowlist of the methods direct mode has ever
  actually implemented, not a `subscriptions/listen`-specific denylist — is recorded in
  [ADR 0014's Amendment section](../../adr/0014-negotiated-mcp-client-interoperability.md) and in
  `docs/specifications/0.4.2/i1-dual-mode-mcp-transport.md` §10.1/§11.1/§28. This record's I1 §3.1
  table and exit statement below are updated accordingly, and the regression suite was re-run in full
  at `6461db6d51ee29e9c973e62b005aa84d5d95c077` — a genuine re-verification, not a citation-only rebind.

## Regression suite (full local run at `RELEASE_CANDIDATE_SHA`)

| Suite | Result |
|---|---|
| `uv run ruff check .` | clean |
| `uv run ruff format --check .` | clean |
| `uv run pytest tests/unit` | 1001 passed |
| `uv run pytest tests/integration` | 288 passed |

288 integration tests = the 287 count at `71e2d8b` + 1 new subprocess-isolated regression test,
`tests/integration/test_mcp_direct_marker_dos_regression.py::test_subscriptions_listen_cannot_hang_the_server`,
added by the guard fix (PR #145) to prove the exact real-world `subscriptions/listen` reproduction now
terminates within a strict, OS-enforced timeout instead of hanging the server. The 1001 unit count
(+3 over 998) reflects that same fix's added coverage in `tests/unit/test_mcp_discovery.py` (an
unimplemented-method rejection check for a second method, a header/body-mismatch-priority check, and
a post-rejection server-health check) net of one removed check that was not actually fail-bounded
(review finding, see below), plus unrelated unit coverage from PRs #142/#143 that merged into `main`
in the same commit range (evidence-reference validation, OpenAPI version metadata) — neither of which
touches I1's transport behavior.

## I1 §3.1 required items

| Item | Evidence |
|---|---|
| Direct mode (unchanged v0.4.0 envelope) | `tests/unit/test_mcp_discovery.py::test_mcp_protocol_and_discovery` — all pre-existing `_check_*` helpers exercising the direct envelope |
| Direct-marked method allowlist (I3.3 correction, spec §10.1) | `tests/unit/test_mcp_discovery.py`'s `_check_another_unimplemented_direct_marked_method_is_also_rejected` (proves the fix is a general allowlist, not a `subscriptions/listen`-specific denylist entry — the other real Claude Code method observed, `server/discover`, is rejected the same way), `_check_header_body_mismatch_takes_priority_over_unimplemented_method`, `_check_server_stays_responsive_after_rejecting_an_unimplemented_direct_method`; `tests/integration/test_mcp_direct_marker_dos_regression.py::test_subscriptions_listen_cannot_hang_the_server` (the exact `subscriptions/listen` reproduction, run in a genuinely separate OS process with an OS-enforced socket timeout — an in-process `asyncio.wait_for` check cannot bound this hang, since the offending SDK code never yields to the event loop) |
| Negotiated mode | `tests/unit/test_mcp_discovery.py`'s `_check_markerless_initialize_reaches_negotiated_sdk_path`, `_check_negotiated_tools_call_shares_the_direct_tool_implementation` |
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

> GO — At `6461db6d51ee29e9c973e62b005aa84d5d95c077` (`RELEASE_CANDIDATE_SHA`, re-frozen by I3.2 after
> `71e2d8b954fa92430723fced302baa3666255397`'s invalidation), AIP's direct (`2026-07-28`) and
> negotiated MCP transport modes remain semantically equivalent: identical `ArchitectureAnswer`
> results for equivalent requests, identical snapshot/evidence continuity in both cross-mode
> directions, identical Origin/Host protection, and identical non-POST rejection behavior. Neither
> mode issues a session identifier (`NOT_APPLICABLE` for conditional-session qualification). Zero
> graph writes occur across every I1 routing path — direct and negotiated, success and rejection, for
> all three tools — proven in one consolidated test rather than only per-tool. A direct-marked request
> naming a method outside the closed allowlist AIP has ever actually implemented for direct mode
> (`tools/list`, `tools/call`) is now rejected with a clean `METHOD_NOT_FOUND` (-32601) rather than
> blindly forwarded to the mounted SDK app — closing the single-request denial-of-service found during
> I3.3 actual-client qualification (a real Claude Code client's legitimate `subscriptions/listen`
> traffic hung the server indefinitely under the pre-fix candidate). I1 blockers = 0.
