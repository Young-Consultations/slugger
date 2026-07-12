# ADR-0016: Codex Coding-Agent Adapter Strategy

**Date:** 2026-07-12
**Status:** Accepted

## Context

The `CodexProvider` (CC-001 era) used the OpenAI chat-completions API with a code-focused system prompt.  While functional, this conflates two distinct concerns:

1. **Code-model completions** — stateless, single-turn generation via `/v1/chat/completions`.
2. **Coding-agent execution** — stateful, workspace-level code tasks (write files, run commands, iterate).

The CC-005 task requires an explicit Codex coding-agent adapter for use cases where the agent must modify files in a controlled workspace, run commands, and produce auditable transcripts.

## Decision

**Adopt the controlled `codex exec` adapter pattern** via an `ICodexAgentClient` contract (see `providers/codex_agent_client.py`).

Key design choices:

| Concern | Decision |
|---|---|
| Interface shape | `ICodexAgentClient` with `start_task`, `continue_task`, `review`, `retrieve_events`, `terminate` |
| Session identity | Every task has an explicit `session_id`; resume is supported by passing the same ID to `continue_task` |
| Workspace safety | All file writes and commands are gated through `CodexWorkspace.is_path_allowed` and `is_command_allowed` |
| Test strategy | `FakeCodexAgentClient` provides deterministic behaviour with no network access |
| Naming clarity | `CodexProvider` is re-classified in comments as "OpenAI code-model provider"; `ICodexAgentClient` is the true agent adapter |
| Live adapter | Opt-in via environment variable; disabled by default |

The OpenAI Python Agents SDK and `mcp-server` integration remain the **preferred future upgrade** once the SDK is stable.  The adapter pattern means the code-generation, review, and refactoring agents are isolated from the transport choice.

## Alternatives considered

| Option | Reason rejected |
|---|---|
| Agents SDK + `mcp-server` | SDK still in beta; `mcp-server` requires a running Codex CLI process with authenticated session |
| Direct subprocess `codex` CLI | Tight coupling, harder to mock, session management is manual |
| Keep chat-completions only | Does not satisfy CC-005 requirement for workspace-level agency and audit trail |

## Consequences

* `CodexProvider` continues to serve stateless code completions (renamed/re-documented, not deleted).
* All workspace-level code tasks route through `ICodexAgentClient`.
* `FakeCodexAgentClient` is mandatory in test environments; live adapter is opt-in.
* `CodexWorkspace` enforces path and command allow-lists; violations raise `PermissionError`.
* Any future SDK upgrade only requires a new `ICodexAgentClient` implementation.
