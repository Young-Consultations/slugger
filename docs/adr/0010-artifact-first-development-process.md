# ADR 0010: Artifact-First Development Process

Status: Accepted

## Context

Traditional software projects often treat code as the primary deliverable, with documentation, architecture records, and traceability artifacts produced late or omitted. For an AI Software Factory, this approach is inadequate:
- AI agents need structured, well-defined artifacts as inputs and outputs.
- Traceability from requirements to code is essential for quality assurance.
- Generated artifacts must be reviewable, diffable, and version-controlled.
- Workflows must be able to validate that each phase has produced its required outputs before proceeding.

## Decision

Adopt an **artifact-first development process** in which documentation, specifications, architecture, and planning artifacts are produced *before* implementation begins.

The canonical order of artifact production for any Slugger-managed project:

1. **Vision** — problem statement, goals, and success criteria.
2. **Requirements** — functional and non-functional requirements.
3. **User Stories** — user-facing scenarios and acceptance criteria.
4. **Architecture** — system design, component boundaries, data flows.
5. **ADRs** — architectural decisions and their rationale.
6. **Planning** — milestones, sprint plans, dependencies.
7. **Interfaces** — public contracts and API definitions.
8. **Implementation** — source code following declared interfaces.
9. **Tests** — unit, integration, and validation tests.
10. **Documentation** — updated guides, references, and changelogs.
11. **Deployment** — CI/CD pipelines, release packages.

Artifacts are typed objects stored in `artifacts/` with metadata for traceability. Every artifact links back to the requirement or workflow step that produced it.

## Consequences

**Positive:**
- Complete traceability from idea to deployed software.
- Agents have well-defined inputs (previous artifacts) and outputs (new artifacts).
- Quality gates can validate artifact completeness before proceeding.
- Documentation is never an afterthought.
- Audit trails are automatically generated as a byproduct of execution.

**Negative:**
- Requires discipline to maintain the artifact-first sequence under time pressure.
- More artifacts means more storage and management overhead.
- Early-stage exploration may feel constrained by required artifact production.
