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

# Epic 6: Prompt Lifecycle

**Epic priority:** P0/P1

## Epic Goal

Manage prompts as versioned, approved, tested, and traceable engineering assets.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-035: Register repository prompt files as versioned assets

**Priority:** P0  
**Implementation order:** 35  
**Estimated complexity:** Medium  
**Depends on:** WP-016

### Objective

Load system, task, and template Markdown prompts into `PromptRegistry` using validated metadata and content hashes.

### Background and Current-State Gap

Prompt lifecycle exists in memory while repository prompt files are not automatically registered and many lack documented version metadata.

### Scope and Likely Files

- prompts/lifecycle.py
- prompts/README.md
- prompts/system/*.md
- prompts/templates/*.md
- validators/prompt_evaluator.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define prompt frontmatter with ID, version, type, owner, status, description, inputs, outputs, model constraints, and change notes.
2. Scan configured directories and register exact hashes.
3. Migrate existing system/templates without changing intent.
4. Treat work packets as executable task assets.
5. Detect duplicate IDs, invalid versions, missing variables, and unversioned approved changes.
6. Persist or deterministically rebuild registry state.
7. Add migration and failure tests.

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

- All maintained prompts load successfully.
- Approved prompt changes require version change and review.
- Registry history is reproducible.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_prompt_lifecycle.py tests/test_prompt_evaluation.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-035`
- Commit: `Implement WP-035: Register repository prompt files as versioned assets`
- Pull request: `WP-035 — Register repository prompt files as versioned assets`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-036: Resolve and pin prompts during agent execution

**Priority:** P0  
**Implementation order:** 36  
**Estimated complexity:** High  
**Depends on:** WP-035, WP-010

### Objective

Require provider-backed agents to resolve an approved prompt ID/version, validate rendering, and record exact provenance.

### Background and Current-State Gap

Agents construct prompt/content internally, bypassing versioning, approval, regression, and reproducibility.

### Scope and Likely Files

- agents/base.py
- models/agent.py
- models/execution.py
- prompts/lifecycle.py
- orchestrator/bootstrap.py
- workflow/executor.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add prompt references to agent capability metadata.
2. Inject a prompt resolver.
3. Require approved versions in production and allow drafts only in development.
4. Validate expected variables and reject missing/unexpected values.
5. Record prompt ID/version/hash, rendered-input hash, and status.
6. Remove duplicated inline prompts where managed assets exist.
7. Test pinning, draft rejection, variables, resume, and version changes.

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

- Every provider-backed execution references an exact managed prompt.
- Resume uses the originally pinned prompt unless invalidated.
- Production rejects unapproved substitutions.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_agent_contracts.py tests/test_prompt_lifecycle.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-036`
- Commit: `Implement WP-036: Resolve and pin prompts during agent execution`
- Pull request: `WP-036 — Resolve and pin prompts during agent execution`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-037: Enforce prompt evaluation and regression in CI

**Priority:** P0  
**Implementation order:** 37  
**Estimated complexity:** Medium  
**Depends on:** WP-035, WP-036

### Objective

Run structural evaluation and deterministic regression baselines for all approved prompts and fail CI on unauthorized drift.

### Background and Current-State Gap

Prompt evaluator/regression code exists but repository prompt changes are not an enforced CI gate.

### Scope and Likely Files

- validators/prompt_evaluator.py
- validators/prompt_regression.py
- prompts/
- .github/workflows/ci.yml
- scripts/

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Create a command that evaluates all registered prompts and emits JSON/Markdown.
2. Create reviewed baselines for approved system/templates.
3. Classify versioned change, quality regression, variable-contract change, and unauthorized drift.
4. Run the command in CI with clear annotations.
5. Add an explicit reviewed baseline-update command.
6. Test unchanged, approved change, accidental drift, missing baseline, and variable regression.

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

- Approved prompt drift fails CI.
- Intentional versioned changes update baselines through a documented review step.
- Baselines contain no rendered secrets or live model output.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_prompt_evaluation.py tests/test_prompt_regression.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-037`
- Commit: `Implement WP-037: Enforce prompt evaluation and regression in CI`
- Pull request: `WP-037 — Enforce prompt evaluation and regression in CI`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-038: Add structured ChatGPT prompt review policy

**Priority:** P1  
**Implementation order:** 38  
**Estimated complexity:** Medium  
**Depends on:** WP-005, WP-037

### Objective

Combine deterministic prompt rules with structured ChatGPT review and human approval under a versioned quality policy.

### Background and Current-State Gap

ChatGPT prompt review and local scoring exist separately and do not produce one explainable governance decision.

### Scope and Likely Files

- services/chatgpt/client.py
- services/chatgpt/models.py
- prompts/lifecycle.py
- validators/prompt_evaluator.py
- workflow/approvals.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define review dimensions for objective, context, constraints, IO contract, testability, safety, ambiguity, and maintainability.
2. Parse typed findings with severity/confidence.
3. Combine model and deterministic results under versioned policy.
4. Require human approval for system prompts and unresolved high findings.
5. Store review metadata/hashes without sensitive content.
6. Handle malformed/failed model reviews as non-pass.
7. Add deterministic mock tests.

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

- Mandatory rule failures always block approval.
- Model disagreement remains visible.
- A prompt cannot approve itself.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_chatgpt_service.py tests/test_prompt_lifecycle.py tests/test_prompt_evaluation.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-038`
- Commit: `Implement WP-038: Add structured ChatGPT prompt review policy`
- Pull request: `WP-038 — Add structured ChatGPT prompt review policy`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-039: Complete prompt approval, deprecation, and changelog

**Priority:** P1  
**Implementation order:** 39  
**Estimated complexity:** Medium  
**Depends on:** WP-035, WP-038

### Objective

Implement protected prompt states, deprecation/replacement rules, and a generated prompt changelog.

### Background and Current-State Gap

Approval concepts exist but ownership, transition policy, deprecation, and repository changelog are incomplete.

### Scope and Likely Files

- prompts/lifecycle.py
- workflow/approvals.py
- agents/support/changelog_agent.py
- docs/generator.py
- cli/main.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define allowed transitions by prompt type/environment.
2. Require owner, reviewer, rationale, quality evidence, and effective version.
3. Add deprecation metadata, replacement, and removal target.
4. Prevent new production selection of deprecated prompts while preserving historical resume.
5. Generate prompt changelog by version and consumers.
6. Expose status through CLI/report.
7. Test transition, replacement, retirement, and resume.

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

- All transitions are validated and auditable.
- Deprecated prompts provide replacement guidance.
- Historical runs remain reproducible.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_prompt_lifecycle.py tests/test_approval_gates.py tests/test_prompt_regression.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-039`
- Commit: `Implement WP-039: Complete prompt approval, deprecation, and changelog`
- Pull request: `WP-039 — Complete prompt approval, deprecation, and changelog`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-040: Capture prompt execution provenance and effectiveness

**Priority:** P1  
**Implementation order:** 40  
**Estimated complexity:** Medium  
**Depends on:** WP-036, WP-047, WP-048

### Objective

Link prompt executions to agent, provider/model, context, outputs, quality outcome, latency, usage, and cost.

### Background and Current-State Gap

Prompt and observability components exist but prompt effectiveness and execution provenance are not unified.

### Scope and Likely Files

- models/execution.py
- prompts/lifecycle.py
- observability/models.py
- observability/cost_tracker.py
- observability/telemetry.py
- models/artifact_lineage.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define prompt-execution records with redacted hashes and correlation IDs.
2. Instrument every provider-backed prompt execution.
3. Link context snapshot, produced artifacts, retries, and downstream outcomes.
4. Record latency, usage, cost, validation score, and review findings.
5. Add queries/reporting by prompt version, agent, workflow, and provider.
6. Define retention/redaction policy.
7. Test correlation across retry and resume.

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

- Every provider-backed prompt has a provenance record.
- Operators can compare prompt versions without exposing sensitive content.
- Retries and resumes remain distinguishable.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_cost_tracking.py tests/test_prompt_lifecycle.py tests/test_telemetry.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-040`
- Commit: `Implement WP-040: Capture prompt execution provenance and effectiveness`
- Pull request: `WP-040 — Capture prompt execution provenance and effectiveness`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
