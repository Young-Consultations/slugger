# CC-005: Replace the fake Codex wrapper with a true Codex coding-agent adapter

**Milestone:** M2 — Real AI agents  
**Priority:** P0  
**Implementation order:** 5  
**Depends on:** CC-002, CC-003

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

Integrate a real Codex coding-agent surface capable of inspecting a workspace, editing files, running approved commands, reviewing changes, and continuing a bounded session.

## Verified current-state problem

- `CodexProvider` calls `/chat/completions` and returns text.
- `CodeGeneratorAgent`, review agent, and refactor agent do not use Codex.
- The current implementation is not an agentic repository coding loop.

## Primary scope and likely files

- providers/codex_provider.py
- providers/base.py
- services/
- agents/development/code_generator_agent.py
- agents/development/code_review_agent.py
- agents/development/refactor_agent.py
- config/settings.py
- tests/test_codex_provider.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Write an ADR selecting one supported integration: preferred Python Agents SDK + Codex CLI `mcp-server`; acceptable alternative is a controlled `codex exec` adapter.
2. Create a `CodexAgentClient` contract for start task, continue task, review, retrieve events, and terminate.
3. Implement workspace root, permissions, allowed commands, timeout, session/thread ID, and resume support.
4. Rename or reclassify the current chat-completions wrapper as a generic OpenAI code-model provider; do not label it a full Codex agent.
5. Connect code generation, review, and refactoring agents to the Codex-agent capability.
6. Parse agent events/results into structured file changes, command evidence, findings, and usage metadata.
7. Add a deterministic fake Codex process/MCP adapter for tests.
8. Add opt-in live smoke tests that operate only in a disposable fixture workspace.

## Prompt-engineering requirements

- Use the managed prompts from CC-002 as task briefs and review criteria.
- Require Codex to return a final machine-readable completion summary with changed files, commands, tests, unresolved issues, and session ID.
- Do not accept prose claiming tests passed without command evidence.

## Software-engineering requirements

- Do not expose Codex execution in untrusted/public environments.
- Use explicit permissions and a disposable allowed workspace.
- Block commands outside an allowlist and preserve a transcript/evidence log.

## Acceptance criteria

- A deterministic integration test shows Codex-agent behavior modifying a fixture workspace.
- Code review returns prioritized structured findings without silently changing files.
- Refactor operates only on approved findings and allowed paths.
- The old fake-Codex behavior is no longer selected as the coding agent.

## Required validation

- `python -m pytest tests/test_codex_provider.py tests/test_orchestration_pipeline.py -q`
- `python -m pytest -q`
- Opt-in disposable live Codex smoke test

## Pull-request evidence

- ADR
- Codex agent contract/adapter
- Fake adapter
- Workspace and transcript evidence

## Out of scope

- Codex cloud provisioning
- Public execution endpoint
- Unbounded shell access

## Rollback requirement

Disable the live adapter through configuration and retain the deterministic fake; never restore the misleading provider naming.

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

- Branch: `copilot/cc-005`
- Commit: `CC-005: Replace the fake Codex wrapper with a true Codex coding-agent adapter`
- Draft PR: `CC-005 — Replace the fake Codex wrapper with a true Codex coding-agent adapter`
