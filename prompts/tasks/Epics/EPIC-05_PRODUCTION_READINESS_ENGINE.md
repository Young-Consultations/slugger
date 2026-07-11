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

# Epic 5: Production Readiness and Generated-App Delivery

**Epic priority:** P0

## Epic Goal

Materialize, build, test, scan, document, score, and release a runnable Python application.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-027: Materialize generated artifacts into safe workspace

**Priority:** P0  
**Implementation order:** 27  
**Estimated complexity:** High  
**Depends on:** WP-003, WP-016

### Objective

Write approved generated file artifacts into an isolated project workspace atomically and reproducibly.

### Background and Current-State Gap

The system models artifacts but does not yet prove that an idea becomes a runnable project on disk.

### Scope and Likely Files

- services/project_materializer.py
- models/project.py
- models/artifact.py
- config/settings.py
- orchestrator/orchestrator.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define workspace lifecycle and materialization result models.
2. Create unique project/run staging and final workspaces.
3. Revalidate paths, symlinks, file types, sizes, and duplicates at write time.
4. Write staging files, verify checksums, and atomically publish.
5. Generate a file manifest mapping paths to artifact versions.
6. Support clean rebuild, resume, and failed-workspace evidence.
7. Test traversal, partial writes, restart, and deterministic manifests.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Never execute code during materialization.
- Never overwrite an existing user directory.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- A valid artifact set becomes a complete project directory.
- Unsafe paths cannot escape or corrupt the workspace.
- Every file maps to an immutable artifact version.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_project_materializer.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-027`
- Commit: `Implement WP-027: Materialize generated artifacts into safe workspace`
- Pull request: `WP-027 — Materialize generated artifacts into safe workspace`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-028: Implement application template contracts and selection

**Priority:** P0  
**Implementation order:** 28  
**Estimated complexity:** High  
**Depends on:** WP-027, WP-041

### Objective

Define production template manifests for supported Python app types and deterministic selection from project requirements.

### Background and Current-State Gap

Output types are envisioned but code generation is not constrained by a required-file/build/run/deploy contract.

### Scope and Likely Files

- templates/
- models/project.py
- knowledge/standards.py
- config/defaults.yaml
- workflow/recipes/python-project.yaml
- examples/

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define template manifest schema with app type, Python versions, required files, commands, gates, and deployment targets.
2. Implement an approved initial set such as CLI, FastAPI, and Streamlit, or document a narrower accepted set.
3. Select template deterministically from project input.
4. Merge template-owned and generated files using explicit ownership/conflict rules.
5. Validate output against template contract.
6. Create golden sample projects/manifests.
7. Document plugin-style template extension.

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

- Every supported app type has a versioned contract and sample.
- Selection and merge behavior are deterministic.
- Generated projects satisfy required files and commands.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_sample_projects.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-028`
- Commit: `Implement WP-028: Implement application template contracts and selection`
- Pull request: `WP-028 — Implement application template contracts and selection`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-029: Add isolated build and smoke-test runner

**Priority:** P0  
**Implementation order:** 29  
**Estimated complexity:** High  
**Depends on:** WP-027, WP-028

### Objective

Install, build, test, and smoke-run generated projects inside a resource-bounded isolation adapter.

### Background and Current-State Gap

Production readiness cannot be established through static artifact inspection alone.

### Scope and Likely Files

- services/build_runner.py
- models/execution.py
- config/settings.py
- validators/test_gate.py
- agents/qa/test_runner_agent.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define build plan/result models with commands, environment, timeout, output, and hashes.
2. Implement a temporary-virtualenv subprocess adapter.
3. Add an optional container adapter without requiring Docker for unit tests.
4. Allow only template-declared commands and sanitize environment/network.
5. Run install, compile/import, unit, integration, and smoke phases.
6. Capture bounded logs/reports as evidence.
7. Test success, timeout, forbidden command, nonzero exit, output limit, and environment leakage.

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

- A generated sample installs and passes smoke tests.
- Unsafe commands and secrets are blocked.
- Every build phase returns structured evidence.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_build_runner.py tests/test_mandatory_tests.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-029`
- Commit: `Implement WP-029: Add isolated build and smoke-test runner`
- Pull request: `WP-029 — Add isolated build and smoke-test runner`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-030: Integrate coverage measurement and thresholds

**Priority:** P0  
**Implementation order:** 30  
**Estimated complexity:** Medium  
**Depends on:** WP-029

### Objective

Measure generated-project line/branch coverage and enforce template/profile thresholds in readiness.

### Background and Current-State Gap

`CoverageGate` accepts a value but the primary pipeline does not collect or validate coverage evidence.

### Scope and Likely Files

- validators/readiness.py
- validators/test_gate.py
- services/build_runner.py
- config/schema.yaml
- workflow/recipes/full-sdlc.yaml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add coverage tooling to test dependencies and generated template contracts.
2. Collect machine-readable line/branch coverage from isolated runs.
3. Define profile/template thresholds and critical-module overrides.
4. Reject missing or malformed reports.
5. Feed coverage to readiness and remediation findings.
6. Route insufficient coverage to test generation.
7. Test pass, fail, no data, malformed, and critical-file cases.

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

- Coverage evidence matches the exact build manifest.
- Generated projects cannot lower production thresholds.
- Below-threshold coverage blocks release readiness.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_readiness_engine.py tests/test_mandatory_tests.py tests/test_build_runner.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-030`
- Commit: `Implement WP-030: Integrate coverage measurement and thresholds`
- Pull request: `WP-030 — Integrate coverage measurement and thresholds`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-031: Add lint, format, typing, coverage, and CI gates

**Priority:** P0  
**Implementation order:** 31  
**Estimated complexity:** Medium  
**Depends on:** WP-029

### Objective

Expand repository and generated-project quality gates beyond the current pytest-only GitHub workflow.

### Background and Current-State Gap

Current CI does not enforce formatting, linting, typing, or coverage and reports seven pytest collection warnings.

### Scope and Likely Files

- .github/workflows/ci.yml
- pyproject.toml
- services/build_runner.py
- validators/quality_gate.py
- workflow/recipes/full-sdlc.yaml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Configure formatter/linter and type checker with a passing, justified baseline.
2. Rename or mark production `Test*` classes so pytest no longer collects them.
3. Add CI jobs for formatting, lint, types, tests, and coverage.
4. Add equivalent generated-project gates through template/build manifests.
5. Normalize static-analysis findings into readiness evidence.
6. Cache safely and upload non-sensitive failure artifacts.
7. Document local CI-equivalent commands.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Do not use blanket ignores to create a false pass.
- Document every temporary file-specific exclusion.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- All seven collection warnings are resolved.
- CI enforces every configured check.
- Generated-project static failures block readiness.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m ruff check .`.
- Run `python -m ruff format --check .`.
- Run `python -m mypy agents core models orchestrator providers services workflow`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-031`
- Commit: `Implement WP-031: Add lint, format, typing, coverage, and CI gates`
- Pull request: `WP-031 — Add lint, format, typing, coverage, and CI gates`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-032: Integrate source, dependency, and secret scanning

**Priority:** P0  
**Implementation order:** 32  
**Estimated complexity:** High  
**Depends on:** WP-029, WP-031

### Objective

Combine internal rules with supported security, dependency-vulnerability, and secret scanning tools for Slugger and generated apps.

### Background and Current-State Gap

Internal scanner/dependency checker exist, but tool-backed scans and normalized release evidence are incomplete.

### Scope and Likely Files

- validators/security_scanner.py
- services/dependency_checker.py
- services/build_runner.py
- validators/readiness.py
- pyproject.toml
- .github/workflows/ci.yml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define adapters for Python source security, dependency audit, and secret scanning.
2. Run pinned/configured tools inside the build context.
3. Normalize findings with severity, confidence, advisory/rule, file/package, and guidance.
4. Deduplicate overlapping tool findings while retaining evidence.
5. Integrate expiring approval-gated waivers.
6. Run repository scans in CI and generated-app scans in readiness.
7. Add offline fixtures for clean, vulnerable, waived, and tool-failure cases.

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

- Critical/high findings block production without a valid waiver.
- Tool unavailability in production is a failed gate.
- Scan evidence is tied to the exact artifact manifest.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_security_scanning.py tests/test_dependency_updates.py tests/test_readiness_engine.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-032`
- Commit: `Implement WP-032: Integrate source, dependency, and secret scanning`
- Pull request: `WP-032 — Integrate source, dependency, and secret scanning`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-033: Enforce documentation and deployment completeness

**Priority:** P0  
**Implementation order:** 33  
**Estimated complexity:** Medium  
**Depends on:** WP-028, WP-029

### Objective

Generate and validate required documentation, configuration, deployment, monitoring, and operations artifacts per template.

### Background and Current-State Gap

`DocumentationGate` checks names but not template-derived requirements or useful content.

### Scope and Likely Files

- agents/development/documentation_agent.py
- agents/operations/deployment_agent.py
- agents/operations/monitoring_agent.py
- validators/readiness.py
- docs/generator.py
- templates/

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Declare required docs/deployment artifacts in each template manifest.
2. Generate README, architecture, config, API/CLI, testing, deployment, runbook, security notes, and changelog as applicable.
3. Validate required headings, non-placeholder content, links, commands, and examples.
4. Match docs to exact version and template commands.
5. Generate env examples without secrets.
6. Feed findings into readiness/remediation.
7. Add golden sample tests.

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

- Placeholder documents do not count as complete.
- Commands in docs match executable manifests.
- Missing or inconsistent documentation blocks readiness.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_doc_generation.py tests/test_readiness_engine.py tests/test_sample_projects.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-033`
- Commit: `Implement WP-033: Enforce documentation and deployment completeness`
- Pull request: `WP-033 — Enforce documentation and deployment completeness`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-034: Wire readiness evidence to release enforcement

**Priority:** P0  
**Implementation order:** 34  
**Estimated complexity:** High  
**Depends on:** WP-019, WP-025, WP-030, WP-031, WP-032, WP-033

### Objective

Aggregate authoritative evidence, create an explainable release recommendation, and block release/deployment unless mandatory gates and approvals pass.

### Background and Current-State Gap

The readiness engine computes scores from supplied values but does not collect authoritative evidence or enforce release decisions.

### Scope and Likely Files

- validators/readiness.py
- validators/quality_gate.py
- workflow/recipes/full-sdlc.yaml
- agents/operations/release_agent.py
- agents/operations/deployment_agent.py
- scripts/release.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Build an evidence collector for build, tests, coverage, static analysis, security, dependencies, docs, traceability, approvals, and health.
2. Version scoring policy and safe configuration bounds.
3. Separate score from mandatory gate status.
4. Generate JSON/Markdown readiness reports and remediation actions.
5. Add blocked, needs-approval, candidate, and approved states.
6. Ensure candidate hashes remain unchanged through release.
7. Enforce decisions in GitHub release/deployment agents.
8. Test blocked and approved end-to-end paths.

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

- Mandatory failures block release regardless of numeric score.
- An unchanged passing candidate can be approved and released.
- Reports identify every missing or failed requirement.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_readiness_engine.py tests/test_release_automation.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-034`
- Commit: `Implement WP-034: Wire readiness evidence to release enforcement`
- Pull request: `WP-034 — Wire readiness evidence to release enforcement`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
