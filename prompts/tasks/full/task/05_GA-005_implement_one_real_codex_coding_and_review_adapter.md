# GA-005: Implement one real Codex coding and review adapter

**Priority:** P0  
**Implementation order:** 5  
**Depends on:** GA-003, GA-004

## Objective

Provide one production Codex agent for coding, review, refactoring, and session resume.

## Canonical implementation to keep

- `ICodexAgentClient` is canonical.
- One supported live adapter uses Codex CLI/MCP/SDK or controlled `codex exec`.
- `FakeCodexAgentClient` remains test-only.

## Code and behavior to remove

- Delete or rename the misleading chat-completions Codex path.
- Delete duplicate generation/review/refactor provider paths.
- Delete static scaffold fallback from production.

## Primary scope

- providers/codex_provider.py
- services/codex/
- agents/development/
- orchestrator/bootstrap.py
- config/settings.py
- docs/adr/

## Ordered implementation steps

1. Implement start, continue, review, refactor, terminate, and event retrieval.
2. Enforce workspace root, command policy, timeout, and session ID.
3. Connect generation/review/refactor agents.
4. Parse file changes, commands, findings, and usage.
5. Add deterministic fake adapter tests.
6. Add opt-in live disposable-workspace smoke tests.
7. Delete static fallback behavior.

## Definition of Done

- A configured live adapter can modify a disposable workspace.
- Offline tests use only the fake.
- Failure causes retry/escalation, never a static scaffold.
- Review/refactor use the same session-aware adapter.
- No alternate production Codex path remains.

## Required validation

- `python -m pytest tests/test_codex_provider.py tests/test_orchestration_pipeline.py -q`
- `python -m pytest -q`
- Run opt-in Codex smoke test when available.

## Rollback

Disable live adapter and retain fake for tests; never restore static fallback.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-005`
- Commit: `GA-005: Implement one real Codex coding and review adapter`
- Draft PR: `GA-005 — Implement one real Codex coding and review adapter`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
