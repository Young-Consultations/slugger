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

# Epic 7: Knowledge Base

**Epic priority:** P1/P2

## Epic Goal

Retrieve and enforce standards, patterns, and approved lessons.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-041: Bootstrap and persist engineering knowledge index

**Priority:** P1  
**Implementation order:** 41  
**Estimated complexity:** Medium  
**Depends on:** WP-016

### Objective

Create a production knowledge service, index repository knowledge at startup, and cache versioned index state.

### Background and Current-State Gap

Knowledge indexer and standards repository exist but bootstrap does not establish a durable knowledge lifecycle.

### Scope and Likely Files

- knowledge/indexer.py
- knowledge/standards.py
- knowledge/README.md
- orchestrator/bootstrap.py
- orchestrator/context.py
- config/settings.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Create a knowledge service combining document index and standards repository.
2. Index configured Markdown/YAML with hashes and schema version.
3. Persist cache metadata and rebuild only changed documents.
4. Expose health, counts, categories, duration, and errors in diagnostics.
5. Fail production startup when mandatory standards are missing/invalid.
6. Test initial build, incremental update, deletion, invalid source, and restart.

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

- Bootstrap exposes a healthy knowledge service.
- Incremental indexing is deterministic.
- Missing mandatory standards fail clearly.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_knowledge_indexing.py tests/test_standards_repository.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-041`
- Commit: `Implement WP-041: Bootstrap and persist engineering knowledge index`
- Pull request: `WP-041 — Bootstrap and persist engineering knowledge index`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-042: Implement policy-aware knowledge retrieval

**Priority:** P1  
**Implementation order:** 42  
**Estimated complexity:** High  
**Depends on:** WP-041, WP-010

### Objective

Retrieve a bounded, explainable set of standards, patterns, decisions, templates, and lessons for each agent execution.

### Background and Current-State Gap

Lexical search exists but agents do not receive governed knowledge context with citations and mandatory-standard guarantees.

### Scope and Likely Files

- knowledge/indexer.py
- knowledge/standards.py
- agents/support/knowledge_agent.py
- orchestrator/context.py
- models/execution.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define retrieval request/result models by capability, phase, project constraints, and artifact types.
2. Rank mandatory standards first and use deterministic tie-breaking.
3. Apply count, character/token, category, and sensitivity limits.
4. Return excerpts with path, heading, hash, and score.
5. Attach citations to context snapshots and outputs.
6. Handle no results and stale index.
7. Test relevance, mandatory inclusion, limits, citations, and ordering.

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

- Relevant bounded knowledge reaches agent context.
- Mandatory standards cannot be omitted by query wording.
- Retrieval is deterministic and cited.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_knowledge_indexing.py tests/test_agent_memory.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-042`
- Commit: `Implement WP-042: Implement policy-aware knowledge retrieval`
- Pull request: `WP-042 — Implement policy-aware knowledge retrieval`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-043: Enforce standards across SDLC artifacts

**Priority:** P1  
**Implementation order:** 43  
**Estimated complexity:** High  
**Depends on:** WP-042, WP-012

### Objective

Convert mandatory standards from passive context into machine/reviewer checks, remediation, waivers, and release evidence.

### Background and Current-State Gap

The standards repository can mark standards mandatory but workflow gates do not consistently enforce them.

### Scope and Likely Files

- knowledge/standards.py
- validators/quality_gate.py
- validators/artifact_validator.py
- agents/planning/*.py
- agents/architecture/*.py
- agents/development/code_review_agent.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Map standards to agents, artifact types, templates, and phases.
2. Inject mandatory clauses into generation/review.
3. Implement deterministic validators where possible.
4. Require reviewer conformance decisions for non-machine-checkable standards.
5. Record satisfied, violated, waived, and not-applicable status.
6. Route violations to remediation and approval-gated waivers.
7. Include conformance in manifest/readiness.

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

- Every candidate has standards evidence.
- Violations block or route to remediation/approval.
- Waivers are version-bound and expire.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_standards_repository.py tests/test_orchestration_pipeline.py tests/test_readiness_engine.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-043`
- Commit: `Implement WP-043: Enforce standards across SDLC artifacts`
- Pull request: `WP-043 — Enforce standards across SDLC artifacts`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-044: Capture approved lessons from reflection

**Priority:** P2  
**Implementation order:** 44  
**Estimated complexity:** Medium  
**Depends on:** WP-041, WP-025

### Objective

Turn workflow reflection into reviewed, versioned lessons without allowing automatic self-modification.

### Background and Current-State Gap

Reflection agent and lessons directory exist but no governed publication path connects them.

### Scope and Likely Files

- agents/support/reflection_agent.py
- knowledge/lessons-learned/
- knowledge/indexer.py
- workflow/approvals.py
- prompts/lifecycle.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define lesson proposal with problem, evidence, components, recommendation, confidence, and target path.
2. Generate proposals on completion and terminal failure.
3. Deduplicate against existing lessons and link source runs.
4. Require human approval before publication.
5. Version the published document and rebuild index.
6. Verify retrieval in a later fixture.
7. Test proposal, duplicate, rejection, approval, publication, and retrieval.

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

- Only approved lessons enter canonical knowledge.
- Published lessons are versioned and traceable.
- Agents cannot directly edit standards or system prompts.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_knowledge_indexing.py tests/test_approval_gates.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-044`
- Commit: `Implement WP-044: Capture approved lessons from reflection`
- Pull request: `WP-044 — Capture approved lessons from reflection`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-045: Add optional semantic retrieval with fallback

**Priority:** P2  
**Implementation order:** 45  
**Estimated complexity:** High  
**Depends on:** WP-041, WP-042, WP-008

### Objective

Support embedding/hybrid retrieval through provider contracts while preserving deterministic lexical fallback.

### Background and Current-State Gap

Embedding capability exists but knowledge retrieval is lexical and semantic use could create a live-provider dependency if not designed carefully.

### Scope and Likely Files

- knowledge/indexer.py
- providers/base.py
- providers/registry.py
- config/settings.py
- observability/cost_tracker.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define embedding index adapter with model/version and chunk hashes.
2. Chunk Markdown deterministically by headings.
3. Build/cache embeddings only when configured.
4. Combine lexical and semantic scores under versioned policy.
5. Fallback to lexical on outage, budget, or stale index.
6. Record usage/cost/model version.
7. Test fake-vector ranking, invalidation, fallback, and model change.

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

- Semantic retrieval remains optional.
- Mandatory lexical standards retrieval always works.
- Index invalidates on content/model change.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_knowledge_indexing.py tests/test_provider_contracts.py tests/test_cost_tracking.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-045`
- Commit: `Implement WP-045: Add optional semantic retrieval with fallback`
- Pull request: `WP-045 — Add optional semantic retrieval with fallback`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-046: Complete knowledge quality gates and contributor guide

**Priority:** P2  
**Implementation order:** 46  
**Estimated complexity:** Low  
**Depends on:** WP-041, WP-042, WP-043, WP-044

### Objective

Validate knowledge metadata, ownership, links, contradictions, duplication, and freshness in CI.

### Background and Current-State Gap

Knowledge can influence every generated app but is not governed like prompts and code.

### Scope and Likely Files

- knowledge/
- validators/knowledge_validator.py
- .github/workflows/ci.yml
- tests/test_knowledge_quality.py
- knowledge/README.md

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define metadata for standards, patterns, decisions, and lessons.
2. Validate IDs, versions, owners, status, applicability, mandatory flags, and review dates.
3. Detect duplicate IDs, broken links, conflicting mandatory standards, and stale content.
4. Add CI command/report.
5. Document authoring, review, deprecation, and lesson publication.
6. Add valid/invalid fixtures.

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

- All canonical knowledge passes validation.
- Conflicting mandatory standards fail CI.
- Contributor procedures are documented and tested.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_knowledge_quality.py tests/test_knowledge_indexing.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-046`
- Commit: `Implement WP-046: Complete knowledge quality gates and contributor guide`
- Pull request: `WP-046 — Complete knowledge quality gates and contributor guide`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
