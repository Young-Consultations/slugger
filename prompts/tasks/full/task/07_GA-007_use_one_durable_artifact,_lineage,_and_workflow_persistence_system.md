# GA-007: Use one durable artifact, lineage, and workflow persistence system

**Priority:** P0  
**Implementation order:** 7  
**Depends on:** GA-001, GA-006

## Objective

Make durable SQLite persistence the only production store for artifacts, versions, lineage, state, attempts, and evidence.

## Canonical implementation to keep

- `SQLiteArtifactStore` and one selected SQLite workflow database.
- In-memory stores remain test-only.

## Code and behavior to remove

- Delete production use of in-memory artifact/lineage stores.
- Delete JSON workflow persistence after migration.
- Delete duplicate state databases and unused abstractions.

## Primary scope

- models/artifact_store.py
- models/artifact_version.py
- models/artifact_lineage.py
- workflow/persistence.py
- workflow/state_db.py
- orchestrator/bootstrap.py

## Ordered implementation steps

1. Select one schema and transaction boundary.
2. Provide one-time migration from JSON records.
3. Persist exact consumed-input lineage.
4. Commit state, artifacts, lineage, and events transactionally.
5. Add concurrency, idempotency, backup, restore, and corruption checks.
6. Close connections deterministically.
7. Delete obsolete persistence code.

## Definition of Done

- Data survives restart.
- No unclosed SQLite warnings remain.
- Duplicate workers cannot finish the same attempt.
- Only consumed inputs become parents.
- One production persistence stack remains.

## Required validation

- `python -m pytest tests/test_artifact_versioning.py tests/test_artifact_lineage.py tests/test_workflow_state_db.py tests/test_workflow_persistence.py -q`
- `python -m pytest -q`

## Rollback

Restore the database backup and run the migration rollback.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-007`
- Commit: `GA-007: Use one durable artifact, lineage, and workflow persistence system`
- Draft PR: `GA-007 — Use one durable artifact, lineage, and workflow persistence system`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
