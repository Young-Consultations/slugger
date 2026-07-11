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

# Epic 1: AI Provider Completion

**Epic priority:** P0

## Epic Goal

Connect Codex, ChatGPT, Canva, and GitHub capabilities to the runtime and prove their contracts.

## Execution Guidance

Execute packets in numeric order unless dependencies permit parallel work. Use one GitHub Copilot Agent session and one focused draft pull request per packet. Review the proposed plan before accepting broad changes.

## Epic Exit Criteria

- Every packet Definition of Done is satisfied or deferred through an approved scope decision.
- No P0 requirement in this epic is deferred.
- All new schemas, commands, settings, and runbooks are documented.
- Live integrations have deterministic mocks and opt-in live checks.
- The complete test and CI-equivalent suite passes.

## Work Packets

## WP-001: Define task-oriented provider contracts

**Priority:** P0  
**Implementation order:** 1  
**Estimated complexity:** Medium  
**Depends on:** Repository baseline

### Objective

Extend provider abstractions with typed requests/results for generation, review, refactoring, embeddings, health, and usage.

### Background and Current-State Gap

`BaseProvider` is generic while specialized behavior lives in concrete classes, preventing agents from using a stable capability contract.

### Scope and Likely Files

- providers/base.py
- models/provider.py
- core/contracts.py
- core/capability.py
- providers/mock_provider.py
- tests/test_codex_provider.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Inventory provider and service operations used by agents.
2. Add typed request/result models for text, code, review, refactor, embedding, health, and usage.
3. Add capability discovery and a specific unsupported-capability exception.
4. Keep `complete` and `embed` through compatibility adapters.
5. Update mocks for deterministic results and usage.
6. Add serialization, negotiation, and compatibility tests.

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

- Agents can request capabilities without importing concrete providers.
- Every provider implements or explicitly rejects every typed operation.
- Existing provider behavior remains compatible and tested.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_codex_provider.py tests/test_models.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-001`
- Commit: `Implement WP-001: Define task-oriented provider contracts`
- Pull request: `WP-001 — Define task-oriented provider contracts`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-002: Wire Codex into bootstrap and provider selection

**Priority:** P0  
**Implementation order:** 2  
**Estimated complexity:** Medium  
**Depends on:** WP-001

### Objective

Register and select `CodexProvider` through configuration, bootstrap, project preferences, and capability fallback policy.

### Background and Current-State Gap

`CodexProvider` exists, but bootstrap registers only OpenAI, Anthropic, or mock; development agents still declare mock behavior.

### Scope and Likely Files

- orchestrator/bootstrap.py
- orchestrator/context.py
- config/settings.py
- config/defaults.yaml
- models/project.py
- providers/registry.py
- agents/development/*.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add Codex configuration and environment-backed credential settings.
2. Register Codex during bootstrap when configured.
3. Implement deterministic capability/provider resolution using project preference and fallback order.
4. Inject the resolved provider into development execution.
5. Add a configuration option to prohibit mock fallback in production.
6. Test explicit selection, default selection, missing credentials, and fallback.

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

- `Slugger.status()` reports configured Codex capability and health.
- Development executions record selected provider/model.
- Unavailable mandatory providers fail before downstream work.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_codex_provider.py tests/test_configuration_profiles.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-002`
- Commit: `Implement WP-002: Wire Codex into bootstrap and provider selection`
- Pull request: `WP-002 — Wire Codex into bootstrap and provider selection`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-003: Implement production code-generation artifact pipeline

**Priority:** P0  
**Implementation order:** 3  
**Estimated complexity:** High  
**Depends on:** WP-001, WP-002

### Objective

Connect `CodeGeneratorAgent` to the coding provider and produce a validated multi-file artifact set for a Python application.

### Background and Current-State Gap

The agent currently produces summary content instead of a provider-backed, safe, multi-file application result.

### Scope and Likely Files

- agents/development/code_generator_agent.py
- agents/base.py
- models/artifact.py
- models/execution.py
- workflow/executor.py
- prompts/templates/
- tests/test_orchestration_pipeline.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define a structured generation request from approved requirements, architecture, ADR, design, template, and standards.
2. Create a versioned prompt requiring a machine-readable file manifest.
3. Invoke the coding provider and capture provider/prompt provenance.
4. Parse output into typed source, config, test, docs, and deployment artifacts.
5. Reject absolute paths, traversal, duplicate paths, binary surprises, and secret files.
6. Validate required files and parse all Python before publishing.
7. Add deterministic complete and malformed mock responses.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Treat provider output as untrusted input.
- Publishing must be atomic and idempotent for a run/attempt.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- A generation step returns a coherent multi-file artifact set.
- Unsafe or malformed provider output is rejected without partial publication.
- Every artifact records run, step, prompt, provider, parents, and checksum.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_orchestration_pipeline.py tests/test_codex_provider.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-003`
- Commit: `Implement WP-003: Implement production code-generation artifact pipeline`
- Pull request: `WP-003 — Implement production code-generation artifact pipeline`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-004: Integrate Codex review and bounded refactor loop

**Priority:** P0  
**Implementation order:** 4  
**Estimated complexity:** High  
**Depends on:** WP-003, WP-012

### Objective

Use structured review findings and bounded refactoring iterations until blocking findings are resolved or escalated.

### Background and Current-State Gap

Provider review/refactor methods and agents exist, but are not proven as one traceable closed loop over generated file versions.

### Scope and Likely Files

- agents/development/code_review_agent.py
- agents/development/refactor_agent.py
- providers/codex_provider.py
- workflow/recipes/codex-review-refactor.yaml
- workflow/escalation.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define typed findings with severity, category, file/range, rationale, and remediation.
2. Require structured review output and explicit pass/fail recommendation.
3. Send only approved findings and current file versions to refactoring.
4. Validate patches/replacements against affected-file scope.
5. Re-review until pass or iteration limit.
6. Persist reviews, revisions, superseded versions, and escalation evidence.
7. Test clean, fixable, malformed, and non-converging cases.

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

- Blocking findings cannot be silently waived.
- Non-convergence ends in a manual-intervention state.
- Every finding maps to the exact reviewed and resulting file versions.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_codex_provider.py tests/test_escalation.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-004`
- Commit: `Implement WP-004: Integrate Codex review and bounded refactor loop`
- Pull request: `WP-004 — Integrate Codex review and bounded refactor loop`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-005: Connect ChatGPT prompt execution and review

**Priority:** P0  
**Implementation order:** 5  
**Estimated complexity:** Medium  
**Depends on:** WP-001, WP-035

### Objective

Inject the ChatGPT service into planning and prompt-governance workflows for prompt execution and structured review.

### Background and Current-State Gap

ChatGPT service interfaces, client, models, and mocks exist but are not first-class runtime dependencies.

### Scope and Likely Files

- services/chatgpt/*.py
- orchestrator/bootstrap.py
- orchestrator/context.py
- config/settings.py
- agents/planning/*.py
- prompts/lifecycle.py

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add service settings, credential resolution, timeout, model, and mock mode.
2. Inject `IChatGPTService` into runtime context.
3. Replace planning placeholders with managed prompt execution while keeping deterministic mocks.
4. Convert prompt review into typed quality findings.
5. Capture prompt version, rendered-input hash, model, usage, and decision.
6. Add bounded transient retry and invalid-response handling.
7. Add shared service contract tests.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Use current official OpenAI-supported interfaces; do not preserve invented or obsolete endpoints.
- Do not persist full sensitive prompts/responses by default.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- Planning agents execute through configured ChatGPT or mock service.
- Prompt review is structured and feeds governance.
- Failures are observable and follow workflow policy.
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

- Branch: `feature/wp-005`
- Commit: `Implement WP-005: Connect ChatGPT prompt execution and review`
- Pull request: `WP-005 — Connect ChatGPT prompt execution and review`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-006: Complete Canva design-agent workflow

**Priority:** P0  
**Implementation order:** 6  
**Estimated complexity:** High  
**Depends on:** WP-001, WP-017

### Objective

Register Canva services and agent, resolve/create supported designs, export assets, and feed approved design artifacts into code generation.

### Background and Current-State Gap

Canva client/agent/tests exist, but the agent is omitted from bootstrap and the full workflow does not prove export ingestion or downstream use.

### Scope and Likely Files

- agents/architecture/canva_design_agent.py
- orchestrator/bootstrap.py
- orchestrator/context.py
- services/canva/*.py
- config/settings.py
- workflow/recipes/full-sdlc.yaml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Add OAuth/service configuration, export polling, scopes, and mock mode.
2. Inject `ICanvaService` and register the Canva agent.
3. Create typed design requests from requirements, brand constraints, and screen inventory.
4. Use only officially supported Canva operations; create a manual approval handoff when automation is unsupported.
5. Poll exports with timeout/backoff and ingest assets with MIME, size, checksum, and source metadata.
6. Create design manifest, tokens/style guide, screen inventory, and requirement mappings.
7. Pass approved design artifacts to code generation.
8. Test auth, polling, export failure, ingestion, and full mock handoff.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Verify endpoint support against current official Canva Connect API documentation.
- Feature-flag preview/beta APIs and disable them by default.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- The Canva agent is discoverable in the full SDLC workflow.
- A mock run produces approved design artifacts consumed by development.
- Live mode is configuration-only and failures create actionable states.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_canva_service.py tests/test_canva_design_agent.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-006`
- Commit: `Implement WP-006: Complete Canva design-agent workflow`
- Pull request: `WP-006 — Complete Canva design-agent workflow`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-007: Integrate GitHub repository and workflow automation

**Priority:** P0  
**Implementation order:** 7  
**Estimated complexity:** High  
**Depends on:** WP-003, WP-034

### Objective

Connect generated artifacts and readiness evidence to issues, draft PRs, workflow dispatch, check polling, milestones, and releases.

### Background and Current-State Gap

Low-level GitHub operations and injected service exist, but agents still generate placeholders and no full repository lifecycle is proven.

### Scope and Likely Files

- services/github/*.py
- agents/support/github_issues_agent.py
- agents/operations/ci_cd_agent.py
- agents/operations/release_agent.py
- scripts/release.py
- workflow/recipes/full-sdlc.yaml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Create an idempotent repository-automation layer over low-level calls.
2. Add commands for issue/update, branch/file publication, draft PR, review comments, workflow dispatch/poll, and release.
3. Wire GitHub agents to the injected service.
4. Map workflow packets, findings, approvals, and readiness to GitHub resources.
5. Persist external IDs and update rather than duplicate on resume.
6. Treat failed GitHub checks as release-blocking evidence.
7. Require readiness and final approval before non-draft release.
8. Add complete mock lifecycle tests.

### Technical Requirements

- Use Python 3.11+ and preserve backward compatibility unless a documented migration is included.
- Use typed domain models at subsystem boundaries and dependency injection for runtime services.
- All external calls require explicit timeouts, bounded retry policy, sanitized errors, and deterministic test doubles.
- Unit and integration tests must run without network access or live credentials.
- Persisted schemas require a schema version, migration strategy, atomic writes, and restart/resume tests.
- Never log or persist credentials; redact prompts, source, and personal data according to configuration.
- Update configuration examples, developer documentation, and operator documentation with behavior changes.
- Run focused tests and the complete repository suite before marking the packet done.
- Never force-push or delete branches.
- Do not expose write credentials to untrusted pull-request jobs.

### Out of Scope

- Unrelated refactoring.
- Breaking public APIs without migration and compatibility tests.
- Live-network dependencies in the standard test suite.

### Definition of Done

- A repeated/resumed run does not duplicate issues, PRs, or releases.
- Failed checks block release with actionable evidence.
- All writes support dry-run and least-privilege configuration.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest tests/test_github_expanded.py tests/test_release_automation.py tests/test_orchestration_pipeline.py -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-007`
- Commit: `Implement WP-007: Integrate GitHub repository and workflow automation`
- Pull request: `WP-007 — Integrate GitHub repository and workflow automation`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---

## WP-008: Add provider health, fallback, and contract suite

**Priority:** P0  
**Implementation order:** 8  
**Estimated complexity:** Medium  
**Depends on:** WP-002, WP-005, WP-006, WP-007

### Objective

Provide consistent health checks, fallback policy, shared contract tests, diagnostics, and opt-in live smoke tests.

### Background and Current-State Gap

Availability semantics vary and CI does not prove that real and mock implementations satisfy the same behavior contract.

### Scope and Likely Files

- providers/base.py
- providers/registry.py
- services/*/base.py
- orchestrator/bootstrap.py
- cli/main.py
- tests/test_provider_contracts.py
- .github/workflows/ci.yml

Inspect call sites and modify only files needed to meet acceptance criteria. The file list is guidance, not authorization for broad refactoring.

### Ordered Implementation Tasks

1. Define a shared health result with capability, latency, credential presence, reachability, and sanitized diagnostics.
2. Implement side-effect-free startup health checks.
3. Add configurable fallback order and production prohibition rules.
4. Create reusable provider/service contract tests against all mocks.
5. Add opt-in live tests guarded by markers and environment variables.
6. Add a diagnostics CLI command with redacted output.
7. Document mock, sandbox, and live modes.

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

- All mocks pass the shared contract suite.
- Fallback decisions are deterministic and recorded.
- Live credentials are never required by standard CI.
- Focused tests pass.
- The complete repository test suite passes.
- Documentation and configuration examples are updated.
- The pull request maps each Definition of Done item to evidence.

### Validation Checklist

- Run `python -m pytest -m 'not live' -q`.
- Run `python -m pytest -q`.
- Verify no credential or sensitive payload appears in logs, fixtures, reports, or committed files.
- Verify restart/resume behavior when persistence or workflow state is changed.

### Required Deliverables

- Production source changes.
- Unit and integration tests.
- Configuration and documentation updates.
- Pull-request evidence mapped to the Definition of Done.

### Commit and Pull Request Guidance

- Branch: `feature/wp-008`
- Commit: `Implement WP-008: Add provider health, fallback, and contract suite`
- Pull request: `WP-008 — Add provider health, fallback, and contract suite`
- Record any deferred item as an explicit follow-up issue; never silently omit acceptance criteria.

---
