# ADR 0018: MVP Execution Path

Status: Accepted

## Context

Slugger V1 currently includes a broad full-SDLC workflow engine, multi-agent orchestration, external design integrations, approval gates, readiness gates, and release automation. That path remains useful as a reference implementation, but continuing to extend it while the MVP is being built would couple MVP delivery to systems that are too broad for the initial product slice.

The MVP needs a small, explicit execution path that can be developed and validated independently. This ADR freezes the legacy architecture for non-critical work and defines the boundary between Slugger V1, the MVP, and a future Slugger V2.

## Decision

Slugger will use a dedicated MVP execution path that does not depend on the existing full workflow engine or multi-agent registry. MVP code must live under the `mvp/` package and must not import or call legacy full-SDLC workflow packages.

The primary MVP services are:

1. **Workspace manager** — creates, locates, and cleans isolated workspaces for a run.
2. **Codex adapter** — invokes Codex-oriented coding tasks through the narrow MVP adapter contract.
3. **Project validator** — performs focused validation of project inputs and generated outputs.
4. **Basic runner** — coordinates the minimal MVP execution sequence without the full workflow engine.
5. **GitHub publisher** — publishes MVP outputs to GitHub through a narrow publishing interface.
6. **Run repository** — persists MVP run metadata and status independently of legacy workflow persistence.

The following systems are excluded from the MVP execution path:

- `workflow.engine` and the full workflow runtime.
- `agents.registry` and the legacy multi-agent registry.
- Canva design services, Canva agents, and Canva handoff flows.
- Approval services and durable approval gates.
- Production readiness services and readiness gates.
- Release agents and release automation.

The current multi-agent workflow path is experimental for MVP purposes. It may be used for research, demonstrations, or future V2 design exploration, but it is not the MVP runtime and must not receive new MVP behavior.

Slugger V1 is the existing full-SDLC implementation. The MVP is a constrained product path built alongside V1 with strict dependency boundaries. Slugger V2 may later incorporate lessons from both V1 and the MVP, but V2 decisions must be made explicitly in later ADRs rather than by expanding the MVP into the legacy engine.

Legacy full-SDLC code receives only critical fixes while the MVP is under development. Critical fixes include security, data-loss, repository-breaking, and CI-blocking defects. Feature work for MVP behavior belongs in the MVP path, not in `full-sdlc-v2` or the legacy workflow engine.

An automated architecture dependency test will enforce that Python modules under `mvp/` do not import prohibited legacy packages or services.

## Consequences

- MVP development has a clear architecture boundary and a smaller execution surface.
- The legacy path remains available but is frozen for non-critical MVP expansion.
- Future MVP modules can be added without depending on the full workflow engine, agent registry, Canva, approval, readiness, or release-agent systems.
- Some V1 capabilities will need simplified MVP-specific contracts or deferred implementation rather than reuse through direct imports.
