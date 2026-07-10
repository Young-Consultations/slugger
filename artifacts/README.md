# artifacts/

This directory stores all artifacts produced or consumed by the Slugger system during SDLC execution.

## Purpose

Artifacts are the primary communication medium between agents and phases of the workflow. Every agent should read from and write to this directory rather than maintaining internal state.

## Artifact Types

- `requirements/` — formal requirements documents
- `user_stories/` — user story files
- `architecture/` — architecture diagrams and specifications
- `uml/` — UML diagrams
- `code/` — generated source code
- `tests/` — generated test suites
- `documentation/` — generated technical documents
- `deployment/` — deployment packages and manifests
- `release_notes/` — release note documents
- `risk_register/` — identified risks and mitigations
- `decision_logs/` — records of significant decisions

## Conventions

- Each artifact includes traceability metadata linking it to its source requirements and workflow.
- Artifacts are versioned alongside the project.
- Artifacts are never deleted; superseded artifacts are archived.

## Related

- `agents/` — agents that produce and consume artifacts
- `workflow/` — workflow definitions that specify artifact handoffs
- `state_machine/` — tracks artifact lifecycle state
