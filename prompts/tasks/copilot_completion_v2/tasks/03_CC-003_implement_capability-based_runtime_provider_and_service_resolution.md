# CC-003: Implement capability-based runtime provider and service resolution

**Milestone:** M2 — Real AI agents  
**Priority:** P0  
**Implementation order:** 3  
**Depends on:** CC-001, CC-002

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

Resolve AI and platform capabilities at runtime from project preference, configuration, health, and fallback policy instead of hard-coded `provider='mock'` agent metadata.

## Verified current-state problem

- Bootstrap registers several providers/services, but agent execution does not resolve them.
- Development agents still declare mock providers.
- Project coding-agent preference is reported but not enforced.

## Primary scope and likely files

- providers/base.py
- providers/registry.py
- models/provider.py
- orchestrator/bootstrap.py
- orchestrator/context.py
- config/settings.py
- config/defaults.yaml
- agents/base.py
- tests/test_codex_provider.py
- tests/test_configuration_profiles.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define named capabilities: planning generation, prompt review, code agent, code review, refactor, embeddings, design, repository management, and workflow management.
2. Implement a resolver using required capability, project preference, environment profile, health, and configured fallback order.
3. Inject resolved capability handles into execution context rather than importing concrete providers in agents.
4. Add strict production mode that forbids mock fallback.
5. Record selected implementation, model/tool version, fallback reason, and health state.
6. Add startup diagnostics and clear remediation errors.

## Prompt-engineering requirements

- Prompt requirements declare required capability, not concrete provider class.
- A fallback must not silently change output schema or prompt contract.

## Software-engineering requirements

- Provider selection is deterministic.
- Health checks are bounded and side-effect free.
- Live credentials are not required for standard tests.

## Acceptance criteria

- Configured Codex, ChatGPT, Canva, and GitHub capabilities can be resolved.
- Production mode fails before workflow execution when a mandatory capability is unavailable.
- Development mode uses deterministic mocks only when explicitly allowed.
- Selection/fallback metadata is persisted.

## Required validation

- `python -m pytest tests/test_configuration_profiles.py tests/test_codex_provider.py tests/test_chatgpt_service.py tests/test_canva_service.py tests/test_github_expanded.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Provider-resolution matrix
- Diagnostics output
- Fallback and strict-mode tests

## Out of scope

- Implementing provider-specific task behavior
- Creating new external API endpoints

## Rollback requirement

Restore old bootstrap selection behind a temporary compatibility setting; do not remove strict mode tests.

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

- Branch: `copilot/cc-003`
- Commit: `CC-003: Implement capability-based runtime provider and service resolution`
- Draft PR: `CC-003 — Implement capability-based runtime provider and service resolution`
