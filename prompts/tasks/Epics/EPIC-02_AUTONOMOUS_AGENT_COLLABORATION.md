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

# Epic 2: Autonomous Agent Collaboration

**Epic priority:** P0

## Epic Goal

Turn standalone agents into bounded, traceable engineering feedback loops.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-009: Inject message bus into runtime execution

**Priority:** P0  
**Implementation order:** 9  
**Estimated complexity:** Medium  
**Depends on:** WP-001

### Objective

Make `MessageBus` a run-scoped dependency for agents and workflow steps with correlated event envelopes.

### Background and Current-State Gap

Message publish/subscribe/history exists but is not wired through bootstrap, execution context, or the engine.

### Scope and Likely Files

- agents/messaging.py
- orchestrator/bootstrap.py
- orchestrator/context.py
- models/execution.py
- workflow/executor.py
- agents/base.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add the message bus to application context and run-scoped execution context.
2. Define topics for artifact-ready, review, finding, approval, retry, escalation, and completion.
3. Include run, step, sender, correlation, causation, and artifact references.
4. Prevent subscriber leakage across runs.
5. Record message metadata in telemetry/persistence.
6. Test ordering, isolation, handler failure, and correlation chains.

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

- Agents can publish and consume run-scoped messages.
- Handler failures are isolated and observable.
- Large artifacts are referenced by ID rather than copied.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_agent_messaging.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-009`
- Commit: `Implement WP-009: Inject message bus into runtime execution`
- Pull request: `WP-009 — Inject message bus into runtime execution`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-010: Implement shared project context and memory handoff

**Priority:** P0  
**Implementation order:** 10  
**Estimated complexity:** Medium  
**Depends on:** WP-009

### Objective

Assemble a controlled, versioned project context from approved artifacts, memory, standards, and workflow state for each agent.

### Background and Current-State Gap

Memory exists, but agents mainly receive raw inputs and there is no reproducible context snapshot with access controls.

### Scope and Likely Files

- orchestrator/context.py
- memory/memory_manager.py
- memory/models.py
- models/execution.py
- workflow/executor.py
- agents/base.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define `ProjectContextSnapshot` with metadata, artifact refs, decisions, constraints, findings, and knowledge excerpts.
2. Build a context assembler authorized by agent capability.
3. Apply deterministic size/token limits and prioritization.
4. Persist snapshot metadata and hashes.
5. Write approved outcomes back to project/run-scoped memory.
6. Test project isolation, truncation, deterministic assembly, and resume.

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

- Every agent execution records a reproducible context snapshot.
- Secrets never enter agent context.
- Resume reconstructs the original approved inputs.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_agent_memory.py tests/test_memory.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-010`
- Commit: `Implement WP-010: Implement shared project context and memory handoff`
- Pull request: `WP-010 — Implement shared project context and memory handoff`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-011: Route typed artifacts between agents

**Priority:** P0  
**Implementation order:** 11  
**Estimated complexity:** High  
**Depends on:** WP-003, WP-010, WP-016

### Objective

Resolve workflow inputs by artifact type, version, lineage, and approval status instead of unstructured summaries.

### Background and Current-State Gap

Steps declare inputs/outputs, but downstream agents are not guaranteed the exact approved artifact versions.

### Scope and Likely Files

- workflow/models.py
- workflow/parser.py
- workflow/executor.py
- models/artifact.py
- models/artifact_store.py
- validators/artifact_validator.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Extend input declarations with type, required/optional, selection rule, and approval requirement.
2. Implement deterministic artifact resolution to exact or latest approved compatible version.
3. Fail before execution on missing or ambiguous inputs.
4. Record all consumed artifact IDs/versions in execution and lineage.
5. Prevent rejected, stale, or superseded artifacts from normal consumption.
6. Add parser/resolver tests for all selection modes.

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

- Every step has an explicit consumed-artifact list.
- Invalid dependencies stop before agent execution.
- Recipes can pin versions and approved-latest behavior.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_workflow_engine.py tests/test_artifact_lineage.py tests/test_validators.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-011`
- Commit: `Implement WP-011: Route typed artifacts between agents`
- Pull request: `WP-011 — Route typed artifacts between agents`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-012: Implement architect–developer–reviewer loop

**Priority:** P0  
**Implementation order:** 12  
**Estimated complexity:** High  
**Depends on:** WP-004, WP-011

### Objective

Create a bounded loop where architecture constrains generation, review raises structured findings, and only affected artifacts are revised.

### Background and Current-State Gap

Agents and iterative recipes exist but the main workflow does not prove architecture conformance and targeted invalidation.

### Scope and Likely Files

- workflow/recipes/iterative-review-loop.yaml
- workflow/recipes/full-sdlc.yaml
- agents/architecture/*.py
- agents/development/*.py
- workflow/graph.py
- workflow/escalation.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define loop entry artifacts and exit criteria.
2. Require generation to acknowledge mandatory decisions/constraints.
3. Review architecture conformance and code quality.
4. Route findings with affected files and versions.
5. Invalidate/rerun only affected descendants.
6. Enforce iteration limits and escalation.
7. Produce a collaboration summary with decisions, findings, revisions, and disposition.

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

- A fixture run demonstrates review-driven revision.
- Architecture violations block completion.
- Only affected artifacts are regenerated.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_orchestration_pipeline.py tests/test_task_dependencies.py tests/test_escalation.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-012`
- Commit: `Implement WP-012: Implement architect–developer–reviewer loop`
- Pull request: `WP-012 — Implement architect–developer–reviewer loop`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-013: Implement QA remediation loop

**Priority:** P0  
**Implementation order:** 13  
**Estimated complexity:** High  
**Depends on:** WP-012, WP-029

### Objective

Generate and execute tests against the materialized project, route failures to development, and iterate until mandatory tests pass or escalate.

### Background and Current-State Gap

Test agents produce artifacts but do not complete a feedback cycle against a real generated workspace.

### Scope and Likely Files

- agents/qa/test_generator_agent.py
- agents/qa/test_runner_agent.py
- validators/test_gate.py
- workflow/recipes/full-sdlc.yaml
- workflow/escalation.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Generate tests from requirements, acceptance criteria, interfaces, and risks.
2. Materialize tests into the isolated project workspace.
3. Run mandatory unit, integration, and smoke tests.
4. Convert failures to typed findings with requirement and affected-file links.
5. Route remediation and rerun only necessary stages.
6. Persist reports and remediation history.
7. Test repair success, infrastructure failure, and non-convergence.

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

- A seeded defect is repaired and mandatory tests pass.
- Non-converging failures escalate with evidence.
- Reports map tests to requirements and file versions.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_mandatory_tests.py tests/test_orchestration_pipeline.py tests/test_escalation.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-013`
- Commit: `Implement WP-013: Implement QA remediation loop`
- Pull request: `WP-013 — Implement QA remediation loop`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-014: Implement security remediation loop

**Priority:** P0  
**Implementation order:** 14  
**Estimated complexity:** High  
**Depends on:** WP-013, WP-032

### Objective

Route normalized security findings to bounded code remediation and rescan before release.

### Background and Current-State Gap

The scanner and security agent exist, but findings do not drive a complete file-level remediation/rescan path.

### Scope and Likely Files

- validators/security_scanner.py
- agents/qa/security_review_agent.py
- agents/development/refactor_agent.py
- workflow/recipes/full-sdlc.yaml
- workflow/escalation.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Normalize internal/external scan results.
2. Map findings to file versions, rule/tool, severity, confidence, and guidance.
3. Create a scoped security-remediation prompt.
4. Validate fixes and rescan the complete relevant scope.
5. Allow only approval-gated, expiring waivers.
6. Block release on unresolved critical/high findings.
7. Test remediation, waiver, regression, and non-convergence.

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

- Critical/high findings trigger remediation or a valid waiver.
- Final scan evidence is immutable for the release candidate.
- The coding agent cannot downgrade severity.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_security_scanning.py tests/test_approval_gates.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-014`
- Commit: `Implement WP-014: Implement security remediation loop`
- Pull request: `WP-014 — Implement security remediation loop`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-015: Integrate retry, escalation, and terminal failure handling

**Priority:** P0  
**Implementation order:** 15  
**Estimated complexity:** Medium  
**Depends on:** WP-009, WP-012, WP-013, WP-014

### Objective

Apply escalation policy consistently to provider, validation, generated-code, approval, and infrastructure failures.

### Background and Current-State Gap

Escalation components exist but the engine does not consistently classify and handle failures across subsystem boundaries.

### Scope and Likely Files

- workflow/escalation.py
- workflow/engine.py
- workflow/executor.py
- workflow/models.py
- core/exceptions.py
- config/settings.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define failure categories and retryability rules.
2. Add per-step retry/backoff/escalation policy to the workflow DSL.
3. Persist attempts and escalation decisions.
4. Use idempotency keys for external side effects.
5. Add explicit failed, rejected, cancelled, and manual-intervention states.
6. Create terminal failure evidence/dead-letter records.
7. Test transient recovery, non-retryable failure, exhaustion, timeout, and resume.

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

- No unbounded retry path exists.
- Retry/escalation state survives restart.
- Every terminal failure contains actionable evidence.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_escalation.py tests/test_workflow_engine.py tests/test_workflow_persistence.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-015`
- Commit: `Implement WP-015: Integrate retry, escalation, and terminal failure handling`
- Pull request: `WP-015 — Integrate retry, escalation, and terminal failure handling`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
