"""v0.4.2 I3 - read-only revision-fence CLI helper (spec
`docs/specifications/0.4.2/i3-client-qualification-and-release-preparation.md` §6.3).

Runs read-only, inside the already-running `architecture-intelligence` container, alongside
`check_fixture_state.py`:

    "${COMPOSE[@]}" exec -T architecture-intelligence python \\
        examples/runtime-demo/read_revision_fence.py --json

I3's actual-client qualification procedure (spec §6.2/§6.12) reads `(:AipInternalState).revision`
before and after each client run to prove the client made zero graph writes, independent of whether
the canonical snapshot happens to look the same afterward. This helper is that one read, factored out
of `check_fixture_state.py` rather than requiring every caller to run the full fixture classifier just
to see the fence value.

It performs exactly one read of one scalar in one Bolt query, which is already atomic with respect to
that value - unlike `check_fixture_state.py`'s composite read (whole-database counts, canonical state,
and a separate `get_architecture_drift` call, each its own round trip), this helper has nothing that
could land "between" reads, so it does not need that file's bounded discard-and-retry loop.

A missing `(:AipInternalState)` singleton is a legitimate state on a virgin/EMPTY database (spec
§15.2), not a fencing failure, so it is reported as `{"revision": null}` with exit code 0. But
`read_revision` raises the *same* `RevisionSingletonMissing` for a genuinely corrupted singleton (an
existing node with a null/non-integer/negative/boolean `revision` value) as it does for "no singleton
at all" - so this helper cannot tell those two cases apart from `read_revision` alone, and must not
silently report a corrupted fence as the same `{"revision": null}` used for a legitimately empty
database (spec §6.3: "fail safely on missing/invalid revision state" means never crash or attempt
repair, but it does not mean masking a real corruption as a successful empty read - a caller comparing
`revision_before == revision_after == null` must not be able to accept a client run against a fence it
can't actually trust). It disambiguates the same way `check_fixture_state.py` already does: a true
whole-database node count of `0` is the only thing that makes a missing/invalid revision legitimate;
anything else is reported as a failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Invoked as `python examples/runtime-demo/read_revision_fence.py`, which puts only this file's own
# directory on sys.path - put the repo root back on sys.path explicitly so the `app.*` imports below
# resolve regardless of invocation style (same fixup as check_fixture_state.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.graph.repository import build_driver, open_session
from app.graph.revision_fence import RevisionSingletonMissing, read_revision
from app.settings import load_settings

_CONFIG_PATH = Path(os.environ.get("CONFIG_PATH", "config.yaml"))

_TOTAL_NODE_COUNT_QUERY = "MATCH (n) RETURN count(n) AS count"


class RevisionFenceInvalid(RuntimeError):
    """Raised when the database is non-empty but has no valid `(:AipInternalState)` revision - a
    real corruption, never reported as the same `{"revision": null}` used for a legitimately virgin
    database."""


def read_revision_fence(driver, *, database: str) -> dict[str, int | None]:
    """The Neo4j-backed half of this tool, factored out from `run()` so integration tests can drive
    it directly against a real (e.g. testcontainers) driver without going through `load_settings`'s
    environment-variable contract - same split as `check_fixture_state.py`'s `classify_fixture`."""
    with open_session(driver, database=database, read_only=True) as session:
        try:
            return {"revision": read_revision(session)}
        except RevisionSingletonMissing as exc:
            node_count = session.run(_TOTAL_NODE_COUNT_QUERY).single()["count"]
            if node_count == 0:
                return {"revision": None}
            raise RevisionFenceInvalid(
                f"database contains {node_count} node(s) but has no valid revision fence: {exc}"
            ) from exc


def run() -> dict[str, int | None]:
    settings = load_settings(_CONFIG_PATH)
    driver = build_driver(
        settings.config.graph.uri, settings.secrets.neo4j_user, settings.secrets.neo4j_password
    )
    try:
        return read_revision_fence(driver, database=settings.config.graph.database)
    finally:
        driver.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        required=True,
        help="Emit the revision fence as JSON to stdout (currently the only supported output mode).",
    )
    parser.parse_args(argv)

    try:
        result = run()
    except RevisionFenceInvalid as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
