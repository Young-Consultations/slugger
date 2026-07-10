# ADR 0006: Directory Structure

Status: Accepted

## Context

The Slugger repository is an AI Software Factory with many distinct responsibilities: agent definitions, workflow declarations, artifact storage, prompt management, observability, testing, documentation, and more. Without a deliberate directory structure these concerns would mix, increasing coupling and reducing maintainability.

## Decision

Adopt the standard top-level directory layout defined in `RepositoryContext.md`:

```
agents/         artifacts/      config/         core/
docs/           examples/       knowledge/      logs/
memory/         metrics/        models/         observability/
orchestrator/   plugins/        prompts/        providers/
scripts/        services/       state_machine/  templates/
tests/          validators/     workflow/
```

Each directory has a single, well-defined responsibility documented in its own `README.md`.

## Consequences

- Clear separation of concerns across all system layers.
- New contributors can navigate the repository without prior knowledge.
- Agents, providers, plugins, and workflows can be added without structural changes.
- Each directory's README serves as living documentation of its purpose and conventions.
- The structure supports the plugin architecture, clean architecture, and workflow-driven design adopted in ADRs 0002 and 0003.
