# Standard Header

Before performing any work:

1. Read `prompts/system/MasterOrchestrator.md`.
2. Read `prompts/system/MasterMarketSimulation.md`.
3. Read `prompts/system/RepositoryContext.md`.
4. Read `prompts/system/MasterReasoningFramework.md`.
5. Review applicable ADRs under `docs/adr/`.
6. Inspect current source and tests before proposing changes.
7. Extend working components instead of recreating them.
8. Produce an implementation plan in the pull request description.
9. Keep each work packet to one focused branch and draft pull request.
10. Never commit credentials, generated secrets, or live customer data.

## Verified Repository Baseline

- The repository is Python 3.11 based.
- The existing suite contains 418 passing tests.
- Seven pytest collection warnings remain; WP-031 resolves them.
- Providers, service clients, messaging, approvals, escalation, lineage, versioning, prompt lifecycle, knowledge indexing, readiness scoring, observability, secrets, plugins, and release helpers already exist as components.
- The primary remaining gap is vertical integration into a durable idea-to-production path, replacement of mock defaults, generated-project execution, enforceable release gates, and end-to-end evidence.
- Do not create a duplicate subsystem merely because the existing subsystem is not yet wired into bootstrap or workflows.

# Epic 3: Artifact Traceability

**Epic priority:** P0

## Epic Goal

Persist artifacts, versions, lineage, and requirements-to-release evidence.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-016: Replace in-memory artifact store with durable repository

**Priority:** P0  
**Implementation order:** 16  
**Estimated complexity:** High  
**Depends on:** WP-011

### Objective

Implement durable, versioned artifact storage and retain the in-memory adapter for tests.

### Background and Current-State Gap

Workflow state can persist, but runtime artifacts use `InMemoryArtifactStore` and disappear across process restarts.

### Scope and Likely Files

- models/artifact_store.py
- models/artifact.py
- models/artifact_version.py
- orchestrator/bootstrap.py
- config/settings.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define repository protocol with atomic batch create/read/version/query/checksum operations.
2. Implement a file-backed or SQLite adapter.
3. Separate metadata from large content and verify checksums.
4. Add schema version/migrations.
5. Select durable storage outside test mode.
6. Test concurrency, corruption, restart, and rollback.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Artifacts survive restart/resume.
- Writes are atomic and paths remain under configured storage.
- Corrupt content is detected.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_artifact_versioning.py tests/test_workflow_persistence.py tests/test_artifact_lineage.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-016`
- Commit: `Implement WP-016: Replace in-memory artifact store with durable repository`
- Pull request: `WP-016 — Replace in-memory artifact store with durable repository`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-017: Automatically capture and persist artifact lineage

**Priority:** P0  
**Implementation order:** 17  
**Estimated complexity:** High  
**Depends on:** WP-016

### Objective

Create lineage edges atomically whenever steps consume and produce artifact versions.

### Background and Current-State Gap

`LineageGraph` exists but capture/persistence is not guaranteed by the workflow engine.

### Scope and Likely Files

- models/artifact_lineage.py
- workflow/executor.py
- workflow/engine.py
- models/execution.py
- orchestrator/context.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add lineage repository abstraction and durable adapter.
2. Record source step, agent, prompt, provider execution, and consumed parents for each output.
3. Support derivation, review-of, supersedes, validates, approves, and release-includes relationships.
4. Capture lineage atomically with publication.
5. Reject cycles and cross-project references.
6. Rebuild/verify a graph from persisted records.
7. Add full idea-to-release lineage tests.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Every product artifact has a valid origin path.
- The chain is queryable after restart.
- Artifact and lineage writes cannot diverge.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_artifact_lineage.py tests/test_orchestration_pipeline.py tests/test_workflow_persistence.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-017`
- Commit: `Implement WP-017: Automatically capture and persist artifact lineage`
- Pull request: `WP-017 — Automatically capture and persist artifact lineage`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-018: Integrate artifact versioning and dependency invalidation

**Priority:** P0  
**Implementation order:** 18  
**Estimated complexity:** High  
**Depends on:** WP-017

### Objective

Make artifact versions canonical and mark/rerun affected descendants when upstream approved artifacts change.

### Background and Current-State Gap

Versioning exists independently, so workflows may continue using stale downstream artifacts.

### Scope and Likely Files

- models/artifact_version.py
- models/artifact_store.py
- models/artifact_lineage.py
- workflow/dependencies.py
- workflow/graph.py
- workflow/engine.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Unify repository versions with `ArtifactVersionStore` semantics.
2. Define impact rules by relationship and artifact type.
3. Mark descendants stale on parent change.
4. Compute minimal steps to rerun.
5. Preserve released versions immutably.
6. Require reapproval after material changes.
7. Test patch/minor/major impact, stale resolution, minimal rerun, and deduplication.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Upstream changes mark correct descendants stale.
- Resume reruns only invalidated steps.
- Old releases retain original graphs.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_artifact_versioning.py tests/test_task_dependencies.py tests/test_artifact_lineage.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-018`
- Commit: `Implement WP-018: Integrate artifact versioning and dependency invalidation`
- Pull request: `WP-018 — Integrate artifact versioning and dependency invalidation`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-019: Generate project manifest and traceability matrix

**Priority:** P0  
**Implementation order:** 19  
**Estimated complexity:** Medium  
**Depends on:** WP-017, WP-018

### Objective

Generate JSON and Markdown evidence connecting idea, requirements, decisions, designs, tasks, files, tests, findings, approvals, and release.

### Background and Current-State Gap

Manifest models/tests exist but a complete, enforced matrix is not an output of the primary pipeline.

### Scope and Likely Files

- models/manifest.py
- models/artifact_lineage.py
- docs/generator.py
- workflow/recipes/full-sdlc.yaml
- validators/readiness.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define mandatory manifest sections and stable IDs.
2. Build from persisted artifacts, lineage, executions, approvals, and readiness.
3. Render deterministic JSON and Markdown.
4. Flag missing links, untested requirements, findings, stale artifacts, and unapproved decisions.
5. Attach the manifest to release candidates.
6. Block release when mandatory links are missing.
7. Test complete and incomplete fixture projects.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Every mandatory requirement maps to implementation and test evidence.
- Missing trace links affect readiness.
- Outputs are deterministic.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_project_manifest.py tests/test_artifact_lineage.py tests/test_readiness_engine.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-019`
- Commit: `Implement WP-019: Generate project manifest and traceability matrix`
- Pull request: `WP-019 — Generate project manifest and traceability matrix`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-020: Expose traceability through CLI

**Priority:** P1  
**Implementation order:** 20  
**Estimated complexity:** Medium  
**Depends on:** WP-019

### Objective

Add read-only commands to inspect artifacts, versions, lineage, stale dependencies, and requirement traces.

### Background and Current-State Gap

Operators cannot currently explain why an artifact exists or what remains incomplete without inspecting storage files.

### Scope and Likely Files

- cli/main.py
- orchestrator/orchestrator.py
- models/artifact_lineage.py
- models/manifest.py
- tests/test_cli.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add artifact list/show/version commands.
2. Add ancestor/descendant and stale-item commands.
3. Add `trace requirement <id>` and manifest export.
4. Support text and stable JSON output.
5. Filter by project/run and fail on ambiguity.
6. Redact content by default.
7. Test missing data, JSON, redaction, and export.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Operators can trace any requirement and artifact origin/impact.
- JSON output is automation-safe.
- Sensitive bodies remain redacted by default.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_cli.py tests/test_artifact_lineage.py tests/test_project_manifest.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-020`
- Commit: `Implement WP-020: Expose traceability through CLI`
- Pull request: `WP-020 — Expose traceability through CLI`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-021: Add traceability migration and consistency validation

**Priority:** P1  
**Implementation order:** 21  
**Estimated complexity:** Medium  
**Depends on:** WP-016, WP-017, WP-018, WP-019

### Objective

Protect durable traceability with migrations, consistency checks, repair diagnostics, and restart acceptance tests.

### Background and Current-State Gap

Durable records can become inconsistent after upgrades or interrupted writes without explicit safeguards.

### Scope and Likely Files

- models/artifact_store.py
- models/artifact_lineage.py
- workflow/persistence.py
- workflow/state_db.py
- validators/artifact_validator.py
- scripts/

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Version all persistent trace schemas.
2. Create forward and dry-run migrations.
3. Detect orphan artifacts, missing versions, broken edges, cycles, stale mismatches, and invalid release references.
4. Provide non-destructive repair recommendations.
5. Add old-schema and interrupted-write fixtures.
6. Run, restart, resume, release, and validate an end-to-end graph.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Old fixtures migrate idempotently.
- All seeded corruptions are detected with exact IDs.
- Restart/resume preserves a valid graph.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_artifact_lineage.py tests/test_workflow_state_db.py tests/test_workflow_persistence.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-021`
- Commit: `Implement WP-021: Add traceability migration and consistency validation`
- Pull request: `WP-021 — Add traceability migration and consistency validation`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
