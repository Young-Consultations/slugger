# GA-010: Fix approvals and make one durable approval path

**Priority:** P0  
**Implementation order:** 10  
**Depends on:** GA-007, GA-009

## Objective

Eliminate approval bypass and use one durable, artifact-bound approval system.

## Canonical implementation to keep

- `DurableApprovalStore` and engine-integrated policy are canonical.

## Code and behavior to remove

- Delete in-memory production approvals.
- Delete duplicate handlers after migration.
- Delete resume logic that loses policy or record IDs.

## Primary scope

- workflow/approvals.py
- workflow/engine.py
- workflow/persistence.py
- cli/main.py

## Ordered implementation steps

1. Persist requests, decisions, roles, quorum, expiration, comments, policy version, hashes, and audit events.
2. Bind approvals to immutable evidence.
3. Implement CLI list/show/approve/reject.
4. Invalidate on evidence change.
5. Validate prior decisions during resume.
6. Add append-only integrity checks.
7. Delete obsolete paths.

## Definition of Done

- The resume bypass is impossible.
- Approvals survive restart.
- Quorum and authorization work.
- Changed artifacts invalidate approval.
- One approval system remains.

## Required validation

- `python -m pytest tests/test_approval_gates.py tests/test_workflow_approval_integration.py tests/test_workflow_persistence.py tests/test_cli.py -q`
- `python -m pytest -q`

## Rollback

Pause protected workflows; never auto-approve.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-010`
- Commit: `GA-010: Fix approvals and make one durable approval path`
- Draft PR: `GA-010 — Fix approvals and make one durable approval path`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
