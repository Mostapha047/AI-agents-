#!/usr/bin/env python3
"""Scaffold the local-jobhunter tree. Creates folders and empty files only.

    python template.py                 # create in the current directory
    python template.py --root ~/dev/jh # create somewhere else
    python template.py --dry-run       # show what would happen
    python template.py --bare          # no header comments, truly empty files

Safe to re-run: existing files are never touched, so you can add a path to
STRUCTURE below and run it again to fill in the gap.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# path -> one-line purpose, with the architecture.md section it implements.
STRUCTURE: dict[str, str] = {
    # --- application package -------------------------------------------------
    "jobhunter/__init__.py": "",
    "jobhunter/schemas.py": "§8 — JobPosting, MatchReport, TailoredApplication",
    "jobhunter/cli.py": "§9.2 signal the approval, §4.4 `jobhunter costs`",
    "jobhunter/worker.py": "§9.4 — one process per task queue: --queue jh-untrusted | jh-pii",

    # --- control plane: Temporal CLIENT only. No tokens, no models (§9.8) ----
    "jobhunter/control/__init__.py": "",
    "jobhunter/control/client.py": "§9.8 — start/signal/update/query. Shared by the API and the CLI",

    "jobhunter/api/__init__.py": "",
    "jobhunter/api/main.py": "§9.8 — FastAPI app. Temporal client built once in lifespan",
    "jobhunter/api/auth.py": "§9.8 — bearer token, strict CORS, no cookies. A localhost API is not private",
    "jobhunter/api/schemas.py": "§9.8 — wire contract. Deliberately NOT jobhunter/schemas.py",
    "jobhunter/api/routes/__init__.py": "",
    "jobhunter/api/routes/hunts.py": "§9.8 — POST /hunts, GET status via Query, approve via Update",
    "jobhunter/api/routes/applications.py": "§9.8 — sent signal, draft download. Draft endpoint serves PII",
    "jobhunter/api/routes/costs.py": "§4.4 — ledger report",

    # --- Temporal workflows: deterministic, stdlib imports ONLY (§9.7) -------
    "jobhunter/workflows/__init__.py": "",
    "jobhunter/workflows/hunt.py": "§9.2 — HuntWorkflow: scout → dedupe → normalize → match → approval signal → tailor",
    "jobhunter/workflows/application.py": "§9.2 — ApplicationWorkflow: weeks-long, durable timers, follow-ups",
    "jobhunter/workflows/types.py": "§9.3 — dataclasses crossing the boundary. IDs and verdicts, never text",

    # --- Temporal activities: where all non-determinism lives (§9.1) ---------
    "jobhunter/activities/__init__.py": "",
    "jobhunter/activities/scout.py": "§8 — tier: small, mcp-ats. Queue: jh-untrusted",
    "jobhunter/activities/normalize.py": "§7.2 — zero tools, schema-only. The trust boundary. Queue: jh-untrusted",
    "jobhunter/activities/dedupe.py": "§9.2 — hash comparison, no model call. The biggest cost lever",
    "jobhunter/activities/match.py": "§8 — tier: medium, mcp-profile + mcp-store. Queue: jh-pii",
    "jobhunter/activities/tailor.py": "§8 — tier: large, mcp-profile + mcp-fs. Queue: jh-pii",
    "jobhunter/activities/prep.py": "§8 — tier: large, mcp-ats. Queue: jh-untrusted",
    "jobhunter/activities/idempotency.py": "§9.6 — workflow_id:activity_id keys so retries don't double-count",

    "jobhunter/agents/__init__.py": "",
    "jobhunter/agents/build.py": "§8 — create_agent per role. Checkpointer disabled; event history is the checkpoint",

    "jobhunter/router/__init__.py": "",
    "jobhunter/router/policy.py": "§4.1 Layer 1 — routing.yaml lookup, sensitivity and pii_egress rules",
    "jobhunter/router/middleware.py": "§4.3 — RouterMiddleware.wrap_model_call",
    "jobhunter/router/verifier.py": "§4.2 — Verifier.check, schema-parse-or-escalate",
    "jobhunter/router/ledger.py": "§4.4 — routing_log writes and the cost report",

    "jobhunter/tools/__init__.py": "",
    "jobhunter/tools/client.py": "§5.3 — MultiServerMCPClient against the gateway, scoped by agent identity",

    "jobhunter/store/__init__.py": "",
    "jobhunter/store/db.py": "§10 — postings, matches, applications, routing_log",
    "jobhunter/store/vector.py": "§2 — Chroma index, Ollama embeddings, semantic dedupe",
    "jobhunter/store/audit.py": "§10 — tool_audit, the local mirror of the MCP gateway log",

    # --- MCP servers: separate processes, separate deps (§5.1) ---------------
    "servers/mcp-ats/pyproject.toml": "",
    "servers/mcp-ats/server.py": "§5.2 — fetch_board, list_providers. Touches the internet",
    "servers/mcp-profile/pyproject.toml": "",
    "servers/mcp-profile/server.py": "§5.2 — read_profile, search_profile. Holds PII, never cloud-reachable",
    "servers/mcp-fs/pyproject.toml": "",
    "servers/mcp-fs/server.py": "§5.2 — write_application, list_drafts. Scoped to the drafts directory",
    "servers/mcp-store/pyproject.toml": "",
    "servers/mcp-store/server.py": "§5.2 — query_postings, record_match",

    # --- configuration -------------------------------------------------------
    "config/routing.yaml": "§4 — tiers and tasks",
    "config/egress-gateway.yaml": "§6.2 — key, model allowlist, spend cap, PII block rule",
    "config/mcp-gateway.yaml": "§6.3 — per-agent tool allowlists, description pinning",
    "config/validate.py": "§7.3 — cross-check the two gateway configs. Fails CI on a broken invariant",
    "config/temporal.yaml": "§9.4 — task queues, retry policies, timeouts, the daily Schedule",

    # --- deterministic tests -------------------------------------------------
    "tests/__init__.py": "",
    "tests/test_policy.py": "§4.1 — the PII lane, exhaustively. Highest-consequence file in the repo",
    "tests/test_ledger.py": "§4.4 — budget maths and the degrade threshold",
    "tests/test_dedupe.py": "§9 — hash comparison, the biggest cost lever",
    "tests/test_config_invariants.py": "§7.3 — runs config/validate.py",
    "tests/test_replay.py": "§13.1 — replay saved histories. The only defence against determinism drift",
    "tests/test_api_auth.py": "§9.8 — every endpoint 401s without a token; CORS rejects unknown origins",
    "tests/histories/.gitkeep": "",

    # --- output-quality evals ------------------------------------------------
    "evals/__init__.py": "",
    "evals/test_normalizer_injection.py": "§7.2 — injected posting yields clean fields and zero tool calls",
    "evals/test_tailor_fabrication.py": "§8 — every bullet traces to a profile fact",

    # --- root ----------------------------------------------------------------
    "docker-compose.yml": "§6.4 — the two localhost gateway containers",
    "docs/architecture.md": "The design document this tree implements",
    "requirements.txt": "",
    ".env.example": "The only secret is the provider key, and it belongs to the egress gateway",
    ".gitignore": "",
}

COMMENT_PREFIX = {
    ".py": "#", ".yaml": "#", ".yml": "#", ".toml": "#",
    ".txt": "#", ".example": "#", ".gitignore": "#", ".md": "#",
}


def header_for(path: Path, description: str) -> str:
    """A single comment line, or nothing. Never code."""
    if not description:
        return ""
    key = path.suffix or path.name
    prefix = COMMENT_PREFIX.get(key)
    return f"{prefix} {description}\n" if prefix else ""


def build(root: Path, *, dry_run: bool, bare: bool) -> tuple[int, int]:
    created = skipped = 0

    for relative, description in STRUCTURE.items():
        target = root / relative

        if target.exists():
            print(f"  skip    {relative}")
            skipped += 1
            continue

        content = "" if bare else header_for(target, description)

        if dry_run:
            print(f"  create  {relative}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            print(f"  create  {relative}")
        created += 1

    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="Where to build the tree")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    parser.add_argument("--bare", action="store_true", help="Empty files, no header comments")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    print(f"{'would scaffold' if args.dry_run else 'scaffolding'} into {root}\n")

    created, skipped = build(root, dry_run=args.dry_run, bare=args.bare)

    print(f"\n{created} created, {skipped} already present")
    if skipped and not args.dry_run:
        print("Existing files were left alone. Delete them first if you want them reset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())