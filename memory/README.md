# memory/

This directory contains persistent agent memory, context, and session state used across Slugger workflow runs.

## Purpose

Memory allows agents to retain context between invocations, improving quality and reducing repeated work. This includes short-term session context, long-term learned preferences, and cross-run state.

## Memory Types

| Type | Description |
|------|-------------|
| `session/` | Ephemeral context scoped to a single workflow run |
| `long_term/` | Persistent knowledge and preferences accumulated across runs |
| `vector_store/` | Embedding-based semantic memory for retrieval-augmented generation |
| `cache/` | Cached AI responses to reduce cost and latency |

## Conventions

- Memory files are structured (JSON or YAML).
- Sensitive user data is never stored in memory files committed to version control.
- Session memory is cleared after workflow completion unless explicitly persisted.
- Memory backends are configurable via `config/`.

## Related

- `knowledge/` — curated static knowledge that complements dynamic memory
- `agents/` — agents that read and write memory
- `observability/` — memory access events are captured for auditing
