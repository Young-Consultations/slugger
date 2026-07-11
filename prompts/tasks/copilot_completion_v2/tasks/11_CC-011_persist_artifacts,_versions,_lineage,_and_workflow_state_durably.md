# CC-011: Persist artifacts, versions, lineage, and workflow state durably

**Milestone:** M5 — Auditability  
**Priority:** P0  
**Implementation order:** 11  
**Depends on:** CC-001, CC-007, CC-008

## Copilot Agent assignment

Act as both:
- a senior Python software engineer responsible for executable, secure, maintainable behavior; and
- a senior prompt engineer responsible for versioned, testable, structured AI instructions.

Complete this task in one focused draft pull request.

## Read first

- `prompts/tasks/copilot_completion_v2/MASTER_COPILOT_AGENT_PROMPT.md`
- `prompts/tasks/copilot_completion_v2/OFFICIAL_INTEGRATION_REFERENCES.md` when external services are involved
- Applicable system prompts and ADRs
- Current source and tests named in this task

## Objective

Replace runtime in-memory stores and fragile JSON-only state with versioned, atomic, restart-safe persistence for workflows, artifacts, lineage, attempts, and evidence.

## Verified current-state problem

- Bootstrap uses `InMemoryArtifactStore`.
- Lineage disappears in a new process and currently links all prior artifacts.
- Workflow JSON persistence is incomplete and lacks transactional coordination.

## Primary scope and likely files

- models/artifact_store.py
- models/artifact_version.py
- models/artifact_lineage.py
- workflow/persistence.py
- workflow/state_db.py
- state_machine/persistence.py
- orchestrator/bootstrap.py
- tests/test_artifact_lineage.py
- tests/test_workflow_state_db.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define repository interfaces for artifact content/metadata, versions, lineage, workflow state, attempts, and evidence.
2. Implement a SQLite-backed local production adapter with schema versioning and migrations; retain in-memory adapters for unit tests.
3. Store large content separately when appropriate and verify checksums.
4. Record lineage only from explicitly resolved inputs, not every prior artifact.
5. Use immutable artifact-version IDs and explicit relationships.
6. Commit workflow transition, produced artifacts, lineage, and events transactionally where possible.
7. Add optimistic concurrency/idempotency keys and crash recovery.
8. Add migration, corruption, concurrent-resume, backup, restore, and process-restart tests.

## Prompt-engineering requirements

- Persist prompt/version and provider/session provenance with artifacts.
- Do not persist sensitive raw prompt/source content unless policy permits.

## Software-engineering requirements

- Atomic writes and schema migrations are mandatory.
- Released evidence is immutable.
- A duplicate worker cannot complete the same attempt twice.

## Acceptance criteria

- Artifacts and lineage remain queryable after process restart.
- Lineage reflects only actual consumed parents.
- Approval/build/readiness evidence can reference immutable versions.
- Backup/restore and corruption detection are tested.

## Required validation

- `python -m pytest tests/test_artifact_versioning.py tests/test_artifact_lineage.py tests/test_workflow_state_db.py tests/test_workflow_persistence.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Durable repositories
- Migrations
- Transactional workflow integration
- Recovery tests

## Out of scope

- Cloud database
- Distributed scheduler
- Cross-region replication

## Rollback requirement

Restore from the pre-migration backup and switch adapters through configuration.

## Definition of Done

This task is done only when:

1. Every acceptance criterion has objective evidence in the draft pull request.
2. Every required validation command passes or an explicitly approved platform limitation is documented.
3. The complete repository test suite passes.
4. New behavior is exercised through the primary orchestration path, not only through isolated unit tests.
5. Documentation, configuration examples, prompt metadata, and migrations are updated.
6. No secret, credential, private token, or sensitive generated content appears in committed files or logs.
7. The task has not introduced a duplicate subsystem or an unbounded retry/agent loop.
8. The pull request remains draft until human review is complete.

## Git guidance

- Branch: `copilot/cc-011`
- Commit: `CC-011: Persist artifacts, versions, lineage, and workflow state durably`
- Draft PR: `CC-011 — Persist artifacts, versions, lineage, and workflow state durably`
