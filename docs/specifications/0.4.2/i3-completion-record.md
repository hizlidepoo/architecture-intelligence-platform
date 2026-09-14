# v0.4.2 I3 Completion Record — Actual-Client Qualification and Release Preparation

Spec: [`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md`](i3-client-qualification-and-release-preparation.md)
§12 (Completion Record).

## Before publication

```text
RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0
EVIDENCE_COMMIT_SHA   = 4accf3120712a22b53d34e31a91b446493bcbdf6
```

`DECISION_COMMIT_SHA` is resolved externally after this record's own commit exists (spec §12.1) and is
therefore not embedded here.

### Candidate identity

| Field | Value |
|---|---|
| `RELEASE_CANDIDATE_SHA` | `50862a352626ea38d2fbb36f2ff0ecfc667266d0` |
| Dirty worktree | `false` |
| Dependency-lock SHA-256 (`uv.lock`) | `231ca7f177c4165b6d0d96b47b50d7475250ea79341125979c0781bedbc739f9` |
| Candidate local image ID | `sha256:675605c0dfc6a78e7b1a825c20bfd104926f6e2cbd72c59865681c279b6b2ca5` (local build only, not treated as a stronger identity than the qualified `producer.build_revision` evidence — see [`v0.4.2-rc.3-candidate-preparation.md`](../../release-validation/v0.4.2-rc.3-candidate-preparation.md)) |
| Running candidate `producer.build_revision` result | Exact match to `RELEASE_CANDIDATE_SHA`, confirmed independently by all four actual-client traces and by the rc.3 candidate-preparation record's own live `--serve` verification |

No code, test, dependency, or build-file change has landed since this candidate was frozen — every
commit since is docs/evidence-only (confirmed via `git diff --stat` against `origin/main` covering
`app/`, `tests/`, `examples/runtime-demo/*.sh`, `Dockerfile`, `pyproject.toml`, `uv.lock`). No
candidate-affecting change occurred during I3.3-I3.5, so no further re-freeze was required.

### I1 completion evidence

[`docs/specifications/0.4.2/i1-completion-record.md`](i1-completion-record.md), rebound to
`RELEASE_CANDIDATE_SHA = 50862a352626ea38d2fbb36f2ff0ecfc667266d0` (second genuine behavior-change
rebind, for the negotiated-mode missing-header fallback fix). Exit statement: `0` blockers.

### I2 completion evidence

[`docs/specifications/0.4.2/i2-completion-record.md`](i2-completion-record.md) — unaffected by either
I3.3 or I3.4's transport fixes. Exit statement: `0` blockers.

### Four qualified tuples

| Tuple | Result | Trace |
|---|---|---|
| Codex CLI `0.154.0` | `QUALIFIED` | [`codex-cli.md`](../../release-validation/v0.4.2-client-traces/codex-cli.md) |
| Claude Code CLI `2.1.270` | `QUALIFIED` | [`claude-code.md`](../../release-validation/v0.4.2-client-traces/claude-code.md) |
| Cursor `3.20.17` | `QUALIFIED` | [`cursor.md`](../../release-validation/v0.4.2-client-traces/cursor.md) |
| VS Code `1.137.0` + GitHub Copilot Chat `1.0.84.70.gdb75d0d` | `QUALIFIED` | [`vscode.md`](../../release-validation/v0.4.2-client-traces/vscode.md) |

All four required client families (spec §5) are `QUALIFIED` against the current
`RELEASE_CANDIDATE_SHA`. No client/platform combination not listed in the
[qualified matrix](../../release-validation/v0.4.2-client-qualification.md) is qualified.

### All valid client attempts and infrastructure-invalidated runs

Every tuple's full attempt record — including corrective cycles — is preserved in its own trace, not
aggregated away:

| Tuple | Attempts | Classification of any failed attempt |
|---|---|---|
| Codex CLI | 1 valid attempt | None (clean first attempt against this candidate) |
| Claude Code | 2 valid attempts (one cycle) | Cycle 1: `MODEL_TOOL_SELECTION_FAILURE` (`get_evidence` combined `evidence_refs` with `resolution_evidence_refs`, self-identified while building the I3.5 cross-client matrix and corrected in PR #155) |
| Cursor | 2 valid attempts (one cycle) | Cycle 1: `MODEL_TOOL_SELECTION_FAILURE` (same `evidence_refs` defect, caught by PR #153 review) |
| VS Code | 2 valid attempts (one cycle) | Attempt 1: `MODEL_TOOL_SELECTION_FAILURE` (same `evidence_refs` defect, self-identified before it needed a review round) |

All failed attempts are valid-client attempts per spec §6.5/§6.6 (prerequisites healthy, model tool
selection failed) — none is `INFRASTRUCTURE_FAILURE`, `TRANSPORT_FAILURE`, `CLIENT_CONTROL_FAILURE`,
or `APPROVAL_BLOCKED`. Every tuple's corrective cycle stayed within the LLM-mediated per-cycle budget
of 2 (spec §6.5). **Zero infrastructure-invalidated runs occurred against this candidate.**

### Separate UX observation for all four client families

Executed and recorded for all four (spec §7.2, Appendix A.2), each in a fresh context after protocol
qualification: see each trace's own "Mandatory separate UX observation" section, and the cross-client
summary in [`v0.4.2-client-qualification.md`](../../release-validation/v0.4.2-client-qualification.md#mandatory-separate-ux-observation-spec-72--cross-client-summary).
All four scored `YES` on every §7.2 observation.

### Cross-client mismatch count

```text
Cross-client semantic mismatches:  0
Evidence-meaning mismatches:       0
```

Full field-by-field comparison in
[`v0.4.2-client-qualification.md`](../../release-validation/v0.4.2-client-qualification.md#cross-client-semantic-comparison-spec-71).

### Revision-fence result for every tuple

| Tuple | `revision_after == revision_before` | Fixture-check result |
|---|---|---|
| Codex CLI | PASS (`R = 9` unchanged) | `COMPLETE`, `mismatches: []` |
| Claude Code | PASS (`R = 9` unchanged, covering cycle 1, cycle 2, reconnect, and the UX run) | `COMPLETE`, `mismatches: []` |
| Cursor | PASS on both fixture instances independently (`R = 9` unchanged on each) | `COMPLETE`, `mismatches: []` on each |
| VS Code | PASS (`R = 9` unchanged, one continuous fixture instance covering the entire session) | `COMPLETE`, `mismatches: []` |

**Actual-client revision changes: 0. Post-client fixture mismatches: 0**, across all four tuples.

### Reconnect results

All four tuples successfully disconnected/reconnected and completed one read-only tool call
afterward, per spec §6.11, with the pinned snapshot and confirmed `producer.build_revision` in every
case; see each trace's "Required successful protocol workflow" row 9/10 and the qualified matrix's
"Reconnect result" column.

## §8.3 gate-table result

Every mandatory gate in spec §8.3 is satisfied. Evidence sources:

- The automated/candidate subset (entry conditions, candidate identity, I1/I2 regression, clean-
  checkout suite, evaluator, Architecture Answers + repeatability, dependency audit, version identity,
  CI identity, repository hygiene, candidate-contained link validation) is recorded in
  [`v0.4.2-rc.3-candidate-preparation.md`](../../release-validation/v0.4.2-rc.3-candidate-preparation.md)
  and remains valid — no code, test, or dependency change has landed since.
- The actual-client subset (four qualified tuples, attempt accounting, UX observation, cross-client
  comparison, revision-fence/fixture results, trace sanitization, qualified matrix, README/guide
  links, `docs/mcp.md` re-verification) is recorded above and in
  [`v0.4.2-client-qualification.md`](../../release-validation/v0.4.2-client-qualification.md).
- Evidence-commit link validation (matrix/trace/qualification links resolved at exact
  `EVIDENCE_COMMIT_SHA = 4accf3120712a22b53d34e31a91b446493bcbdf6`) confirmed clean, save for the same
  pre-existing, intentionally GitHub-relative `../../discussions` link in `README.md` already noted as
  out of scope since `rc.1`.
- The full technical evaluation is recorded in
  [`v0.4.2-go-no-go.md`](../../release-validation/v0.4.2-go-no-go.md).

### Test counts (recorded as evidence, not a permanent contract constant)

```text
uv run ruff check .                     -> All checks passed!
uv run ruff format --check .            -> 259 files already formatted
shellcheck examples/runtime-demo/*.sh   -> clean
uv run pytest tests/unit -q             -> 1001 passed
uv run pytest tests/integration -q      -> 288 passed
uv run --with pip-audit pip-audit       -> No known vulnerabilities found
evaluation run (relation-fact evaluator) -> 10/10 PASS
evaluation answers --candidate-sha      -> 23/23 PASS, repeatable (byte-identical hash across 2 runs)
```

### Version result

`pyproject.toml`, `uv.lock`, `app.version.package_version()`, `mcp_server.version`, the production
`Producer.version`, and the evaluation runner's `Producer` all report `0.4.2`; `schema_version`
remains `"0.4"` throughout. See `v0.4.2-rc.3-candidate-preparation.md`'s "Version and package
metadata" section.

### CI/security result

All required checks (`lint + test`, `dependency security scan`, `analyze (actions)`,
`analyze (python)`) `completed`/`success` at the exact `RELEASE_CANDIDATE_SHA`, verified via the
GitHub API against that SHA. See `v0.4.2-rc.3-candidate-preparation.md`'s "CI identity" section.

### Repository hygiene result

All seven prohibited classes checked against the frozen candidate worktree — no unresolved finding
(4 `gitleaks` hits, all confirmed pre-existing false positives already noted in `rc.1`/`rc.2`). See
`v0.4.2-rc.3-candidate-preparation.md`'s "Repository hygiene" section.

## Artifact paths

```text
matrix path:         docs/release-validation/v0.4.2-client-qualification.md
GO/NO-GO path:        docs/release-validation/v0.4.2-go-no-go.md
release-notes path:   docs/release-validation/v0.4.2-release-notes.md
```

## Technical state

```text
RELEASE_READY
```

Every mandatory gate in spec §8.3 is satisfied; `0` release blockers.

## Publication

```text
NOT_PUBLISHED
```

Publication requires separate, explicit repository-owner authorization (spec §10.4) — this record
does not itself authorize or perform tag creation, GitHub Release publication, or any other
publication action.
