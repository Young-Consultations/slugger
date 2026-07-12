# GA-011: Create one readiness and release-gate engine

**Priority:** P0  
**Implementation order:** 11  
**Depends on:** GA-008, GA-009, GA-010

## Objective

Build readiness only from authoritative persisted evidence.

## Canonical implementation to keep

- `ReleaseGateCollector` and one versioned readiness policy are canonical.

## Code and behavior to remove

- Delete standalone/manual scoring paths.
- Delete release agents that bypass gates.
- Delete duplicate quality-gate models.

## Primary scope

- validators/readiness.py
- validators/quality_gate.py
- release/
- agents/operations/release_agent.py
- agents/operations/deployment_agent.py
- models/manifest.py

## Ordered implementation steps

1. Collect build, test, coverage, lint, type, security, dependencies, docs, traceability, standards, approvals, health, budget, packaging, and smoke evidence.
2. Freeze candidate hash.
3. Separate mandatory gates from score.
4. Generate JSON/Markdown reports.
5. Block on missing/changed evidence.
6. Connect to workflow and GitHub.
7. Delete alternate readiness paths.

## Definition of Done

- Broken candidates are blocked with exact gates.
- Passing unchanged candidates reach release-candidate.
- Any file change invalidates readiness/approval.
- No agent bypasses the gate.
- One policy remains.

## Required validation

- `python -m pytest tests/test_readiness_engine.py tests/test_release_automation.py tests/test_project_manifest.py tests/test_approval_gates.py -q`
- `python -m pytest -q`

## Rollback

Invalidate candidate and return to validated-not-ready.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-011`
- Commit: `GA-011: Create one readiness and release-gate engine`
- Draft PR: `GA-011 — Create one readiness and release-gate engine`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
