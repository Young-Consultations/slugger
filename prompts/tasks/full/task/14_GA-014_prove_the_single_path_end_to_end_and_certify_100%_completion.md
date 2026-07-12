# GA-014: Prove the single path end to end and certify 100% completion

**Priority:** P0  
**Implementation order:** 14  
**Depends on:** GA-013

## Objective

Create definitive acceptance evidence proving the canonical path satisfies every in-scope requirement.

## Canonical implementation to keep

- The canonical path established by GA-001 through GA-013.
- One requirements catalog and one certification report.

## Code and behavior to remove

- Delete fake acceptance tests that exercise disconnected components.
- Delete unsupported completion claims.

## Primary scope

- tests/acceptance/
- examples/
- docs/production-readiness.md
- docs/operations-runbook.md
- models/manifest.py
- observability/reporter.py

## Ordered implementation steps

1. Create task-tracker CLI and FastAPI scenarios using the real orchestrator, persistence, materializer, runner, readiness engine, and mock external adapters.
2. Restart mid-run and resume.
3. Inject provider failure, Canva handoff, Codex defect, failing test, security issue, approval rejection, and GitHub check failure.
4. Verify remediation or correct terminal state.
5. Install and smoke-run generated apps.
6. Verify traceability, approvals, readiness, package, SBOM, rollback, and draft release.
7. Create a canonical requirements catalog.
8. Generate a machine-derived completion report.
9. Require 100% of committed in-scope requirements and all P0 requirements.
10. Document only explicitly out-of-scope future roadmap items as limitations.

## Definition of Done

- One clean-checkout command proves the complete offline path.
- Both generated apps install and run.
- Restart/resume and all seeded failures pass.
- No fake runner or disconnected factory is used.
- The report shows 100% in-scope completion with evidence.
- Only one documented execution path remains.

## Required validation

- `python -m pytest tests/acceptance -q`
- `python -m pytest -q`
- Run all CI-equivalent commands.
- Install the wheel and run full offline acceptance.
- Generate the certification report.

## Rollback

Do not certify; preserve the latest passing candidate and publish blockers.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-014`
- Commit: `GA-014: Prove the single path end to end and certify 100% completion`
- Draft PR: `GA-014 — Prove the single path end to end and certify 100% completion`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
