# Claude Code — Actual-Client Trace (I3.3)

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](../../specifications/0.4.2/i3-client-qualification-and-release-preparation.md)
§5 (Qualified Client Tuple Contract), §6 (Actual-Client Qualification Procedure), Appendix B.

## Result: **FAILED** — root cause: product defect (transport disambiguation), not client incompatibility

This is not "Claude Code failed to qualify." A real, current, fully spec-compliant MCP client sent an
ordinary request as part of its normal connection handshake, and that request hung AIP's entire
server. The defect is fixed (ADR 0014's "Amendment" section); this tuple must be requalified against
the new post-fix `RELEASE_CANDIDATE_SHA` before it can be marked `QUALIFIED`.

## Tuple identity

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

## Pre-client state (spec §6.2/§6.3)

`examples/runtime-demo/mcp-demo.sh --serve` with `BUILD_REVISION`/`RELEASE_CANDIDATE_SHA` pinned to
the (then-believed-good) candidate. Fixture checker `COMPLETE`, `mismatches: []`,
`snapshot_id = aip:snapshot:v1:685a34157b6842b00d7130b8490df63060c3d80871c2ed6f56cd9206e62342d8`,
revision fence `R = 9`.

## Attempt record (spec §6.5/§6.6)

| Attempt | Classification | Outcome |
|---|---|---|
| 1 | `TRANSPORT_FAILURE` | `claude mcp add ...` succeeded; `claude mcp list`'s own connectivity health-check hung the server indefinitely instead of completing |

This is a **valid client attempt** per §6.5 (the I2 fixture/server/network prerequisites were healthy
at the moment the client made its request) that fails the tuple with `TRANSPORT_FAILURE`
("prerequisites healthy enough to assess the client, but initialization, protocol exchange, or
reconnect failed") — not `INFRASTRUCTURE_FAILURE`, because the failure is not independent of the
request the client sent; it is a direct, deterministic consequence of that request.

## Root-cause isolation

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

## Sanitized reproduction

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

## Sanitization statement (spec §6.15)

The passive capture contained no authorization headers, bearer tokens, cookies, API keys, refresh
tokens, account identifiers, email addresses, personal user identifiers, raw system prompts, or
unrelated conversation/traffic — verified by direct inspection before any excerpt was used here (this
AIP demo endpoint requires no credential at all). The client-identifying string
`User-Agent: claude-code/2.1.270 (sdk-cli)` is retained as legitimate client-version evidence, not a
personal identifier. Raw `.pcap` capture files were ephemeral, used only for this investigation, and
were not retained beyond it.

## Post-client state

The environment was restored to a clean, healthy state after this finding (container restarted,
fixture torn down) before proceeding. No I2 fixture, revision-fence, or snapshot-continuity claim is
made for this attempt — it never reached a successful tool call, so §6.12's post-client write/state
gate does not apply to a `TRANSPORT_FAILURE` result.

## Disposition

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
