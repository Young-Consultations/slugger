# ADR 0017: Canonical Execution Path

Status: Accepted

## Context

Slugger accumulated multiple workflow and runtime variants while the platform
was evolving. Those alternates created ambiguity about which path was
production-ready and encouraged silent fallbacks when callers omitted explicit
configuration. GA-001 freezes a single architecture so builds, persistence,
approvals, and generated artifacts all follow one durable execution path.

## Decision

Slugger's canonical workflow is `full-sdlc-v2`. The canonical persistence
stack is `SQLiteArtifactStore` for artifact durability and
`DurableApprovalStore` for approval durability. The canonical build runner is
`IsolatedBuildRunner`, and the canonical generated-application representation
is `AppManifest`.

The runtime must prefer this single execution path and reject silent fallbacks
to superseded workflows. In particular, `full-sdlc` is no longer a valid
default for `Slugger.build`.

## Rationale

A single execution path reduces ambiguity, makes regression detection easier,
and prevents the system from quietly routing work through outdated runtime
variants. Explicit failure is preferred over implicit fallback when callers
request superseded workflows.

## Consequences

- `full-sdlc-v2` is the only default workflow for `Slugger.build`.
- `workflow/recipes/full-sdlc.yaml` is archived as a historical recipe.
- Production persistence is standardized on `SQLiteArtifactStore` and
  `DurableApprovalStore`.
- Generated application execution is standardized on `IsolatedBuildRunner`.
- Generated application artifacts are standardized on `AppManifest`.
