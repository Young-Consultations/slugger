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

# Epic 4: Human Approval System

**Epic priority:** P0/P1

## Epic Goal

Pause, approve, reject, audit, and resume protected workflow transitions.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-022: Extend workflow DSL with approval policies

**Priority:** P0  
**Implementation order:** 22  
**Estimated complexity:** Medium  
**Depends on:** WP-011

### Objective

Allow recipes and environment profiles to declare approvers, quorum, timing, and rejection behavior for protected checkpoints.

### Background and Current-State Gap

Approval handler logic exists but approval policy is not a complete first-class recipe/runtime contract.

### Scope and Likely Files

- workflow/approvals.py
- workflow/models.py
- workflow/parser.py
- config/schema.yaml
- config/profiles.py
- workflow/recipes/full-sdlc.yaml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add approval policy schema to recipes and profiles.
2. Support before/after-step checkpoints and severity/artifact triggers.
3. Define roles, quorum, expiration, timeout action, and rejection route.
4. Validate policies at recipe load time.
5. Add development and production defaults.
6. Insert requirements, architecture/design, security, and release checkpoints into full SDLC.

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

- Approval checkpoints are declarative and validated.
- Production profiles cannot silently weaken mandatory gates.
- Policies serialize with workflow state.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_approval_gates.py tests/test_validators.py tests/test_configuration_profiles.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-022`
- Commit: `Implement WP-022: Extend workflow DSL with approval policies`
- Pull request: `WP-022 — Extend workflow DSL with approval policies`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-023: Pause and resume workflows at approval gates

**Priority:** P0  
**Implementation order:** 23  
**Estimated complexity:** High  
**Depends on:** WP-022, WP-015

### Objective

Integrate approvals with engine/state persistence so protected transitions pause durably and resume exactly once after a valid decision.

### Background and Current-State Gap

Approval records exist independently but the engine does not prove a durable pause/resume transition around checkpoints.

### Scope and Likely Files

- workflow/engine.py
- workflow/approvals.py
- workflow/models.py
- workflow/persistence.py
- state_machine/engine.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add awaiting-approval states for workflows and steps.
2. Evaluate checkpoints before protected transitions.
3. Persist pending records and return without marking failure.
4. Validate decision actor/role/quorum, artifact version, and expiry before resume.
5. Apply rejection routing and timeout escalation.
6. Make repeated resume idempotent.
7. Test approve, reject, expire, stale artifact, restart, and duplicate decision.

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

- No protected step runs before approval.
- Modified artifacts invalidate earlier approvals.
- Valid decisions resume exactly once after restart.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_approval_gates.py tests/test_workflow_persistence.py tests/test_state_machine.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-023`
- Commit: `Implement WP-023: Pause and resume workflows at approval gates`
- Pull request: `WP-023 — Pause and resume workflows at approval gates`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-024: Add approval management CLI

**Priority:** P0  
**Implementation order:** 24  
**Estimated complexity:** Medium  
**Depends on:** WP-023

### Objective

Provide list, show, approve, reject, and comment commands for pending approval checkpoints.

### Background and Current-State Gap

A human-in-the-loop workflow lacks an operator surface in the current CLI.

### Scope and Likely Files

- cli/main.py
- orchestrator/orchestrator.py
- workflow/approvals.py
- tests/test_cli.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add `approvals list/show/approve/reject` commands.
2. Require run/checkpoint, actor, role, rationale, and optional evidence.
3. Show exact artifact versions, expiry, quorum, and downstream impact.
4. Require explicit production confirmation in non-interactive mode.
5. Return stable JSON and meaningful exit codes.
6. Test authorization, stale versions, duplicate decisions, rejection, and JSON output.

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

- Every pending approval can be completed through CLI.
- CLI never bypasses policy checks.
- All decisions are auditable and sensitive bodies are redacted.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_cli.py tests/test_approval_gates.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-024`
- Commit: `Implement WP-024: Add approval management CLI`
- Pull request: `WP-024 — Add approval management CLI`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-025: Persist immutable approval audit evidence

**Priority:** P0  
**Implementation order:** 25  
**Estimated complexity:** Medium  
**Depends on:** WP-023, WP-024

### Objective

Store append-only approval requests, decisions, actors, policy evaluations, artifact hashes, and comments as release evidence.

### Background and Current-State Gap

Current audit behavior is not a durable, integrity-checked production record.

### Scope and Likely Files

- workflow/approvals.py
- workflow/persistence.py
- models/artifact_lineage.py
- observability/telemetry.py
- models/manifest.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define versioned approval audit events.
2. Persist request, decision, rejection, expiry, invalidation, and policy evaluation.
3. Record actor/role, time, correlation, artifact version/hash, policy version, rationale, and evidence.
4. Add append-only integrity checks such as chained hashes.
5. Link events to lineage and manifest.
6. Export JSON/Markdown evidence.
7. Test restart, chronology, and tamper detection.

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

- All approval events survive restart.
- Tampering is detected.
- Release manifests reference exact approval evidence.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_approval_gates.py tests/test_workflow_state_db.py tests/test_project_manifest.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-025`
- Commit: `Implement WP-025: Persist immutable approval audit evidence`
- Pull request: `WP-025 — Persist immutable approval audit evidence`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-026: Complete approval acceptance suite and runbook

**Priority:** P1  
**Implementation order:** 26  
**Estimated complexity:** Low  
**Depends on:** WP-022, WP-023, WP-024, WP-025

### Objective

Prove approval behavior across profiles and document normal, rejection, waiver, timeout, and recovery procedures.

### Background and Current-State Gap

Unit-tested components do not prove policy combinations, restart behavior, and production release protection.

### Scope and Likely Files

- tests/test_approval_gates.py
- tests/test_cli.py
- tests/test_orchestration_pipeline.py
- docs/approval-runbook.md
- config/profiles.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add scenarios for development no-gate, production mandatory gates, quorum, rejection-to-rework, timeout escalation, and artifact invalidation.
2. Prove production release cannot proceed without final approval.
3. Document approval, rejection, waiver, expiry, and recovery.
4. Document actor identity assumptions and audit export.
5. Map scenarios to requirement IDs.

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

- Every documented scenario has an automated test.
- Production release protection is demonstrated through restart.
- The operator runbook is executable.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_approval_gates.py tests/test_cli.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-026`
- Commit: `Implement WP-026: Complete approval acceptance suite and runbook`
- Pull request: `WP-026 — Complete approval acceptance suite and runbook`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
