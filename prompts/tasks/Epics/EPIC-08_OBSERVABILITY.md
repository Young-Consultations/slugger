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

# Epic 8: Observability

**Epic priority:** P1

## Epic Goal

Instrument cost, performance, failures, completion, redaction, and operator reporting.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-047: Create unified execution event schema

**Priority:** P1  
**Implementation order:** 47  
**Estimated complexity:** Medium  
**Depends on:** WP-009

### Objective

Standardize run, step, attempt, agent, provider, artifact, approval, gate, and release events and instrument the primary path.

### Background and Current-State Gap

Telemetry, tracing, logging, and collectors exist separately without one complete correlated schema.

### Scope and Likely Files

- observability/models.py
- observability/telemetry.py
- observability/tracer.py
- observability/logger.py
- workflow/engine.py
- workflow/executor.py
- agents/base.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define versioned lifecycle event types.
2. Require run, step, attempt, correlation, and causation IDs.
3. Instrument start, completion, failure, retry, pause, resume, and cancel.
4. Ensure exact-once or idempotent event emission per persisted transition.
5. Mirror event IDs in structured logs.
6. Test event sequences for success, retry, approval, failure, and resume.

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

- Every workflow transition has a correlated event.
- Event sequences survive resume without duplicates.
- Instrumentation failure cannot corrupt workflow state.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_telemetry.py tests/test_workflow_persistence.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-047`
- Commit: `Implement WP-047: Create unified execution event schema`
- Pull request: `WP-047 — Create unified execution event schema`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-048: Capture provider usage, cost, latency, and budgets

**Priority:** P1  
**Implementation order:** 48  
**Estimated complexity:** Medium  
**Depends on:** WP-001, WP-047

### Objective

Integrate `CostTracker` and token budgeting around every provider/service call and enforce configured limits.

### Background and Current-State Gap

Cost and budget components exist but provider calls do not universally report or consume them.

### Scope and Likely Files

- observability/cost_tracker.py
- observability/token_budget.py
- providers/*.py
- services/chatgpt/client.py
- orchestrator/context.py
- config/settings.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Extract provider-reported usage into typed results.
2. Instrument calls with timing, retry, and cost.
3. Add run/phase/step/agent/provider budgets.
4. Reserve estimated budget and reconcile actual usage.
5. Block or escalate hard-limit violations and warn on soft limits.
6. Version pricing policy and distinguish actual from estimated cost.
7. Test retry accounting, missing usage, warning, hard block, and resume.

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

- All provider calls produce latency/usage records.
- Budgets survive resume and are concurrency-safe.
- Cost reports distinguish estimates.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_cost_tracking.py tests/test_token_budgeting.py tests/test_provider_contracts.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-048`
- Commit: `Implement WP-048: Capture provider usage, cost, latency, and budgets`
- Pull request: `WP-048 — Capture provider usage, cost, latency, and budgets`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-049: Collect workflow performance and completion metrics

**Priority:** P1  
**Implementation order:** 49  
**Estimated complexity:** Medium  
**Depends on:** WP-047

### Objective

Replace generic metrics with typed operational and evidence-backed requirements-completion metrics.

### Background and Current-State Gap

Current collector stores generic records and cannot reliably support operational reporting or a 95% completion claim.

### Scope and Likely Files

- observability/collector.py
- observability/models.py
- workflow/engine.py
- workflow/executor.py
- models/manifest.py
- validators/acceptance_metrics.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define metrics for outcomes, durations, attempts, fallbacks, approvals, artifacts, stale items, gates, and requirement completion.
2. Aggregate by project, workflow, agent, provider, and time window.
3. Compute completion from verified requirements evidence.
4. Instrument engine and evidence collector.
5. Persist or deterministically rebuild metrics.
6. Test labels, aggregation, resume deduplication, and completion math.

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

- The 95% figure is computed from evidence, not self-report.
- Repeated resume does not double-count.
- Snapshots are deterministic.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_observability_dashboard.py tests/test_acceptance_metrics.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-049`
- Commit: `Implement WP-049: Collect workflow performance and completion metrics`
- Pull request: `WP-049 — Collect workflow performance and completion metrics`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-050: Correlate failure analytics and remediation outcomes

**Priority:** P1  
**Implementation order:** 50  
**Estimated complexity:** Medium  
**Depends on:** WP-015, WP-047, WP-049

### Objective

Link failures, retries, escalations, findings, remediation attempts, and final outcomes for actionable analysis.

### Background and Current-State Gap

Failure analytics exists but is not fed by the full failure taxonomy or remediation path.

### Scope and Likely Files

- observability/dashboard.py
- workflow/escalation.py
- core/exceptions.py
- models/artifact_lineage.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Normalize all failure and escalation records.
2. Correlate provider, agent, prompt, artifacts, attempts, and final outcome.
3. Track attempts-to-resolution, recurring failures, top failing steps/providers/prompts, and terminal failures.
4. Distinguish generated-product from Slugger-infrastructure failures.
5. Add filters/export.
6. Test retry, remediation, escalation, approval rejection, and resume.

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

- Every terminal failure traces to attempts and evidence.
- Remediated and unresolved failures are distinct.
- Reports identify recurring hotspots without exposing payloads.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_observability_dashboard.py tests/test_escalation.py tests/test_telemetry.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-050`
- Commit: `Implement WP-050: Correlate failure analytics and remediation outcomes`
- Pull request: `WP-050 — Correlate failure analytics and remediation outcomes`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-051: Expose operational dashboard and reports through CLI

**Priority:** P1  
**Implementation order:** 51  
**Estimated complexity:** Medium  
**Depends on:** WP-048, WP-049, WP-050

### Objective

Provide CLI summaries/exports for status, cost, budgets, performance, failures, approvals, gates, and completion.

### Background and Current-State Gap

Operators need a persisted-data surface rather than reading internal files or objects.

### Scope and Likely Files

- observability/dashboard.py
- observability/reporter.py
- cli/main.py
- orchestrator/orchestrator.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add status, metrics, cost, failures, and report-export commands.
2. Support project/run filters and text/JSON output.
3. Show completion, blocked requirements, approvals, budget, failed gates, and next action.
4. Export Markdown/JSON for PRs and releases.
5. Make reports read-only/reproducible from persistence.
6. Add golden-output and exit-code tests.

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

- Operators can identify current blockers and next actions.
- Exports are stable and work after restart.
- Default output is redacted and bounded.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_cli.py tests/test_observability_dashboard.py tests/test_cost_tracking.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-051`
- Commit: `Implement WP-051: Expose operational dashboard and reports through CLI`
- Pull request: `WP-051 — Expose operational dashboard and reports through CLI`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-052: Implement observability redaction, retention, and reliability

**Priority:** P1  
**Implementation order:** 52  
**Estimated complexity:** Medium  
**Depends on:** WP-047, WP-048, WP-051

### Objective

Make logs, telemetry, metrics, and reports safe, bounded, retained appropriately, and non-disruptive.

### Background and Current-State Gap

Provider prompts, source, tokens, or unbounded logs create security/reliability risk without policy.

### Scope and Likely Files

- observability/logger.py
- observability/telemetry.py
- observability/reporter.py
- config/schema.yaml
- config/settings.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define field-level redaction for credentials, headers, prompt variables, source, paths, and personal data.
2. Redact before persistence/export.
3. Add retention/rotation by event/environment.
4. Bound payload sizes and preserve hashes for truncation.
5. Fail open for non-critical telemetry sink errors while recording local diagnostics.
6. Test seeded secrets, oversized payloads, rotation, and sink failure.
7. Document data handling and cleanup.

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

- Seeded secrets never appear in logs/reports.
- Retention and payload limits are enforced.
- Observability failure does not corrupt workflow state.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_telemetry.py tests/test_secrets_management.py tests/test_observability_dashboard.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-052`
- Commit: `Implement WP-052: Implement observability redaction, retention, and reliability`
- Pull request: `WP-052 — Implement observability redaction, retention, and reliability`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
