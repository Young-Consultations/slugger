# GA-009: Create one bounded remediation engine

**Priority:** P0  
**Implementation order:** 9  
**Depends on:** GA-005, GA-008

## Objective

Use one remediation loop for review, tests, lint/type, dependencies, and security.

## Canonical implementation to keep

- `BoundedRemediationLoop` plus the canonical Codex client.
- One normalized finding model and retry/escalation policy.

## Code and behavior to remove

- Delete placeholder review/refactor/security agents.
- Delete duplicate finding models and loop recipes.
- Delete prose-as-proof paths.

## Primary scope

- remediation/
- agents/development/
- agents/qa/
- workflow/escalation.py
- workflow/recipes/

## Ordered implementation steps

1. Normalize findings.
2. Route approved affected files and evidence to Codex.
3. Re-materialize and rerun affected checks.
4. Enforce bounded attempts.
5. Require separate approval for security waivers.
6. Persist every attempt.
7. Delete overlapping loops and placeholders.

## Definition of Done

- A seeded defect is fixed and verified.
- Non-convergence enters manual intervention.
- Critical security cannot be auto-waived.
- Every finding uses one lifecycle.
- One remediation engine remains.

## Required validation

- `python -m pytest tests/test_escalation.py tests/test_security_scanning.py tests/test_mandatory_tests.py tests/test_orchestration_pipeline.py -q`
- `python -m pytest -q`

## Rollback

Restore last passing inventory and retain findings.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-009`
- Commit: `GA-009: Create one bounded remediation engine`
- Draft PR: `GA-009 — Create one bounded remediation engine`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
