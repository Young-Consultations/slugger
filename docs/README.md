# docs/

This directory contains all project documentation, including architecture decisions, specifications, standards, and guides.

## Purpose

Documentation is a first-class deliverable in Slugger. Every architecture decision, interface, workflow, and standard is recorded here to ensure traceability and support long-term maintainability.

## Structure

| Path | Contents |
|------|----------|
| `adr/` | Architecture Decision Records |
| `vision.md` | Product vision statement |
| `roadmap.md` | Feature and milestone roadmap |
| `ai-sdlc-spec.md` | AI-SDLC workflow specification |
| `architecture.md` | System architecture overview |
| `domain-model.md` | Domain model and entity definitions |
| `workflow-dsl.md` | Workflow DSL reference |
| `coding-standards.md` | Python coding standards |
| `design-principles.md` | Design principles and guidelines |
| `security-architecture.md` | Security architecture and threat model |
| `quality-standards.md` | Quality gates and acceptance criteria |
| `testing-strategy.md` | Testing philosophy and strategy |
| `deployment-strategy.md` | Deployment approach and environments |
| `agent-specification.md` | Agent interface and contract specification |

## Conventions

- Documentation is updated alongside every architecture or behavior change.
- ADRs are numbered sequentially and never deleted (deprecated ADRs are superseded).
- All documentation is written in Markdown.

## Related

- `prompts/system/` — AI agent operating guidelines that reference these documents
- `knowledge/` — reusable engineering knowledge and lessons learned
