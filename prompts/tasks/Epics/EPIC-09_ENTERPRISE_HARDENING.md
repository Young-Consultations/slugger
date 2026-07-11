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

# Epic 9: Enterprise Hardening and Certification

**Epic priority:** P0/P1

## Epic Goal

Harden configuration, secrets, persistence, plugins, CI/CD, packaging, acceptance, and certification.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-053: Enforce configuration validation and startup diagnostics

**Priority:** P0  
**Implementation order:** 53  
**Estimated complexity:** Medium  
**Depends on:** WP-008, WP-041

### Objective

Validate profiles, paths, capabilities, storage, workflows, tools, and mandatory production policy before execution.

### Background and Current-State Gap

Configuration/schema/profile components exist but failures may be discovered late in a run.

### Scope and Likely Files

- config/loader.py
- config/settings.py
- config/schema.yaml
- config/profiles.py
- orchestrator/bootstrap.py
- cli/main.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add cross-field validation for providers, services, workflows, storage, approvals, budgets, templates, and policies.
2. Constrain configured paths to allowed roots.
3. Check persistence writeability, recipe validity, knowledge health, provider health, and required tools.
4. Separate warnings from blocking production errors.
5. Add `slugger doctor` with text/JSON remediation guidance.
6. Test invalid profiles, missing tools, unwritable paths, unsupported capabilities, and weakened production policy.

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

- Production fails before execution on missing mandatory dependencies.
- Doctor output is complete and redacted.
- Development fallback must be explicit.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_configuration_profiles.py tests/test_validators.py tests/test_cli.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-053`
- Commit: `Implement WP-053: Enforce configuration validation and startup diagnostics`
- Pull request: `WP-053 — Enforce configuration validation and startup diagnostics`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-054: Harden secrets and OAuth token lifecycle

**Priority:** P0  
**Implementation order:** 54  
**Estimated complexity:** High  
**Depends on:** WP-006, WP-007, WP-053

### Objective

Centralize secure credential resolution, OAuth expiry/refresh, redaction, rotation, and least-privilege diagnostics.

### Background and Current-State Gap

Secrets manager supports env/file lookup but live Canva/GitHub/OpenAI integrations need production token lifecycle controls.

### Scope and Likely Files

- config/secrets.py
- config/settings.py
- services/canva/client.py
- services/github/client.py
- providers/openai_provider.py
- providers/codex_provider.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define secret-provider interface and keep env/file development adapters.
2. Add optional OS keyring/external-store adapter.
3. Model OAuth access/refresh tokens, expiry, and scopes.
4. Implement injectable refresh where supported.
5. Validate least-privilege scopes when available.
6. Centralize header/query redaction and sanitized errors.
7. Support safe rotation/reload.
8. Test precedence, expiry, refresh, failure, file permissions, rotation, and leakage.

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

- All integrations use one managed secret interface.
- Expired tokens refresh or fail clearly.
- No secret appears in repr, logs, telemetry, errors, or reports.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_secrets_management.py tests/test_canva_service.py tests/test_github_expanded.py tests/test_codex_provider.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-054`
- Commit: `Implement WP-054: Harden secrets and OAuth token lifecycle`
- Pull request: `WP-054 — Harden secrets and OAuth token lifecycle`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-055: Harden transactions and concurrent workflow execution

**Priority:** P0  
**Implementation order:** 55  
**Estimated complexity:** High  
**Depends on:** WP-016, WP-021, WP-023

### Objective

Provide atomic cross-record transitions, locking, idempotency, crash recovery, and backup/restore for durable state.

### Background and Current-State Gap

Persistence exists but production use requires duplicate-execution prevention and transaction boundaries across workflow/artifact/lineage/approval records.

### Scope and Likely Files

- workflow/state_db.py
- workflow/persistence.py
- state_machine/persistence.py
- models/artifact_store.py
- models/artifact_lineage.py
- workflow/approvals.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define a unit-of-work per workflow transition.
2. Add optimistic concurrency or locking.
3. Prevent two workers from executing one attempt.
4. Use idempotency keys for external writes and persisted transitions.
5. Recover abandoned attempts/locks after crash.
6. Add backup, restore, and integrity commands.
7. Test duplicate resume, racing approval, racing artifact writes, crash, and restore.

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

- Duplicate workers cannot publish duplicate completions.
- Crash recovery yields resumable or reconciliation state.
- Backup/restore preserves integrity.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_workflow_state_db.py tests/test_workflow_persistence.py tests/test_approval_gates.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-055`
- Commit: `Implement WP-055: Harden transactions and concurrent workflow execution`
- Pull request: `WP-055 — Harden transactions and concurrent workflow execution`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-056: Harden plugin permissions, validation, and isolation

**Priority:** P1  
**Implementation order:** 56  
**Estimated complexity:** High  
**Depends on:** WP-053, WP-055

### Objective

Require plugins to declare capabilities/permissions, validate compatibility/provenance, and receive constrained service facades.

### Background and Current-State Gap

Plugin SDK/packaging exists but plugins remain a high-risk code-execution path without trust and permission policy.

### Scope and Likely Files

- plugins/base.py
- plugins/metadata.py
- plugins/registry.py
- plugins/loader.py
- plugins/sdk.py
- plugins/packaging.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Extend manifests with API compatibility, capabilities, permissions, dependencies, and trust status.
2. Validate packages before import.
3. Require explicit policy for filesystem/network/secrets permissions.
4. Expose constrained facades instead of full context.
5. Add timeout/failure isolation and health disabling.
6. Add checksum/signature provenance hooks.
7. Test traversal, undeclared capability, incompatibility, import failure, and secret access.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Do not claim that in-process Python is a complete security sandbox.
- Document stronger process/container isolation for untrusted plugins.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Invalid/untrusted plugins fail before activation.
- Supported APIs prevent undeclared capability access.
- Plugin failure cannot crash unrelated workflows.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_plugin_sdk.py tests/test_marketplace_packaging.py tests/test_secrets_management.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-056`
- Commit: `Implement WP-056: Harden plugin permissions, validation, and isolation`
- Pull request: `WP-056 — Harden plugin permissions, validation, and isolation`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-057: Complete GitHub CI/CD and release governance

**Priority:** P0  
**Implementation order:** 57  
**Estimated complexity:** High  
**Depends on:** WP-007, WP-031, WP-032, WP-034

### Objective

Create production-grade GitHub workflows, issue/PR templates, Copilot Agent guidance, and protected release automation.

### Background and Current-State Gap

The repository has one pytest workflow and local release preparation only.

### Scope and Likely Files

- .github/workflows/
- .github/ISSUE_TEMPLATE/
- .github/PULL_REQUEST_TEMPLATE.md
- scripts/release.py
- pyproject.toml
- docs/github-operations.md

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add lint/type/test/coverage/security/package jobs with least privilege and concurrency cancellation.
2. Add release workflow that verifies readiness, builds, checksums, SBOM, and draft release.
3. Create issue/PR templates with packet ID, dependencies, files, tests, risks, rollback, and DoD evidence.
4. Add Copilot Agent repository instructions to read system prompts and assigned packet.
5. Protect secrets from untrusted PRs.
6. Define action version/update and artifact retention policy.
7. Validate workflow YAML and release scripts.

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

- CI enforces every mandatory gate.
- Release cannot bypass readiness/final approval.
- Copilot work is branch/draft-PR based and reviewable.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_release_automation.py -q`.
- Run `validate all GitHub workflow YAML files`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-057`
- Commit: `Implement WP-057: Complete GitHub CI/CD and release governance`
- Pull request: `WP-057 — Complete GitHub CI/CD and release governance`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-058: Produce reproducible packages, container, and SBOM

**Priority:** P0  
**Implementation order:** 58  
**Estimated complexity:** High  
**Depends on:** WP-029, WP-031, WP-032, WP-057

### Objective

Build installable distributions and a non-root container with checksums, SBOM, provenance, and smoke tests.

### Background and Current-State Gap

`pyproject.toml` supports installation but production distribution and provenance are incomplete.

### Scope and Likely Files

- pyproject.toml
- Dockerfile
- .dockerignore
- scripts/release.py
- .github/workflows/
- templates/
- docs/deployment.md

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Build source/wheel in clean environment and verify install.
2. Add minimal non-root Slugger container and health command.
3. Define generated-project packaging per template.
4. Generate checksums and SBOM.
5. Record commit, build environment, dependency and readiness hashes.
6. Scan final package/container dependencies where tools are configured.
7. Add practical reproducibility checks.
8. Add package/container smoke tests.

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

- Wheel installs and CLI starts cleanly.
- Container runs non-root and passes health checks.
- Release artifacts include checksums, SBOM, and provenance.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_release_automation.py tests/test_sample_projects.py -q`.
- Run `build and install wheel in a clean environment`.
- Run `build and smoke-test container`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-058`
- Commit: `Implement WP-058: Produce reproducible packages, container, and SBOM`
- Pull request: `WP-058 — Produce reproducible packages, container, and SBOM`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-059: Create full idea-to-production acceptance suite

**Priority:** P0  
**Implementation order:** 59  
**Estimated complexity:** High  
**Depends on:** WP-006, WP-007, WP-013, WP-014, WP-019, WP-023, WP-034, WP-058

### Objective

Prove that an idea produces a runnable, reviewed, tested, traceable, approved, packaged, and releasable Python application.

### Background and Current-State Gap

Extensive component tests do not prove the central business promise across all subsystems.

### Scope and Likely Files

- tests/acceptance/
- examples/
- workflow/recipes/full-sdlc.yaml
- cli/main.py
- orchestrator/orchestrator.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Create at least one CLI and one service/UI acceptance scenario.
2. Use deterministic mock ChatGPT, Codex, Canva, and GitHub through production contracts.
3. Run every phase from project input through release.
4. Restart mid-run and resume.
5. Inject review, test, security, transient provider, rejection, and failed GitHub-check paths.
6. Verify final install/run, lineage, manifest, approvals, readiness, package, SBOM, and release candidate.
7. Add a separate opt-in live-provider smoke scenario.
8. Keep standard fixtures small and network-free.

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

- At least two idea-to-app scenarios pass cleanly.
- Restart/resume and major remediation paths are proven.
- Mandatory evidence is asserted, not just a score.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/acceptance -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-059`
- Commit: `Implement WP-059: Create full idea-to-production acceptance suite`
- Pull request: `WP-059 — Create full idea-to-production acceptance suite`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-060: Publish certification and 95% completion evidence

**Priority:** P0  
**Implementation order:** 60  
**Estimated complexity:** Medium  
**Depends on:** WP-026, WP-034, WP-051, WP-053, WP-057, WP-058, WP-059

### Objective

Generate an evidence-backed requirements report and operational documentation proving at least 95% in-scope completion and 100% P0 completion.

### Background and Current-State Gap

Prior completion estimates were qualitative and must be replaced by stable requirement IDs, automated evidence, known limitations, and release sign-off.

### Scope and Likely Files

- README.md
- docs/ai-sdlc-spec.md
- docs/architecture.md
- docs/production-readiness.md
- docs/operations-runbook.md
- docs/security-runbook.md
- docs/disaster-recovery.md
- models/manifest.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Create canonical requirements catalog from the complete project vision and task set.
2. Assign IDs, priority, owner/component, verification, and mandatory/optional status.
3. Generate completion from tests, manifests, gates, diagnostics, and approved manual checks.
4. Calculate at least 95% of committed scope and require 100% P0.
5. Document limitations, unsupported modes, assumptions, fallbacks, and residual risks.
6. Publish setup, providers, build, approval, release, incident, backup/restore, and rollback runbooks.
7. Create final certification checklist and sign-off artifact.

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

- Completion is at least 95% with all P0 requirements complete.
- Every completed requirement links to evidence.
- Deferred mandatory work prevents certification.
- Final acceptance and CI-equivalent checks pass.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/acceptance -q`.
- Run `python -m pytest -q`.
- Run `run all documented CI-equivalent commands`.
- Run `generate and review certification report`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-060`
- Commit: `Implement WP-060: Publish certification and 95% completion evidence`
- Pull request: `WP-060 — Publish certification and 95% completion evidence`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
