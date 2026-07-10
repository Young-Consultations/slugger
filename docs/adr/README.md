# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Slugger project.

## Purpose

An ADR documents a significant architectural decision: the context that led to it, the options considered, the decision made, and its expected consequences. ADRs create an auditable history of architectural reasoning.

## Conventions

- ADRs are numbered sequentially starting at `0001`.
- File names follow the pattern `NNNN-short-title.md`.
- ADRs are never deleted. Superseded ADRs are updated with a `Superseded by: NNNN` note.
- Status values: `Proposed`, `Accepted`, `Deprecated`, `Superseded`.

## Template

```markdown
# ADR NNNN: Title

Status: Accepted

## Context
Why was this decision needed?

## Decision
What was decided?

## Consequences
What are the positive and negative outcomes?
```

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-project-vision.md) | Project Vision | Accepted |
| [0002](0002-clean-architecture.md) | Clean Architecture | Accepted |
| [0003](0003-plugin-architecture.md) | Plugin Architecture | Accepted |
| [0004](0004-ai-provider-abstraction.md) | AI Provider Abstraction | Accepted |
| [0005](0005-knowledge-first-design.md) | Knowledge-First Design | Accepted |
| [0006](0006-directory-structure.md) | Directory Structure | Accepted |
