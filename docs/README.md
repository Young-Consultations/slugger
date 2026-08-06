# docs/

This directory contains all project documentation, including architecture decisions, specifications, standards, and guides.

## Purpose

Documentation is a first-class deliverable in Slugger. Every architecture decision, interface, workflow, and standard is recorded here to ensure traceability and support long-term maintainability.

## Structure

| Path | Contents |
|------|----------|
| `requirements/` | Authoritative product, software, interface, use-case, business-rule, and traceability requirements baseline |
| `architecture/` | Authoritative software architecture, designs, consolidated decisions, and traceability |
| `mvp.md` | Primary MVP command guide and operations checklist |
| `VISION.md` | Authoritative product vision statement |
| `ai-sdlc-spec.md` | AI-SDLC workflow specification |
| `workflow-dsl.md` | Workflow DSL reference |
| `agent-specification.md` | Agent interface and contract specification |

## Conventions

- Documentation is updated alongside every architecture or behavior change.
- Architectural decisions are maintained in `architecture/ADR.md`; supersession history is retained in that register.
- All documentation is written in Markdown.

## Related

- `prompts/system/` — AI agent operating guidelines that reference these documents
- `knowledge/` — reusable engineering knowledge and lessons learned
