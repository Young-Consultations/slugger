# AI-SDLC extraction assessment

Do not extract the experimental full-SDLC system in this task. Preserve Slugger's focused MVP until the experimental system has a separate execution path, clear ownership, independent tests, independent packaging, and an explicit roadmap.

## Candidate packages

Candidate extraction areas include `agents/`, `workflow/`, `orchestrator/`, `providers/`, `services/`, `state_machine/`, `memory/`, `metrics/`, `observability/`, `materializer/`, `validators/`, `plugins/`, `templates/`, `knowledge/`, and non-MVP prompt libraries under `prompts/`.

## Coupling assessment

- Dependencies on MVP code: MVP tests and docs reference the focused `mvp/` package; extraction must not invert dependencies from `mvp/` into experimental packages.
- Shared models/utilities: `models/`, `core/`, provider interfaces, and prompt templates need ownership decisions before extraction.
- Cyclic dependencies: audit imports between workflow/orchestrator/agents/providers before moving code.
- Configuration coupling: split `config/`, workflow recipes, and environment assumptions into package-owned defaults.
- Test coupling: separate experimental tests from `tests/test_mvp_*` and acceptance tests.
- Packaging implications: define independent `pyproject.toml`, console entry points, dependencies, and release cadence.
- Migration risks: broken imports, duplicated models, unclear ownership, and accidental creation of a second Slugger MVP execution path.

## Recommended extraction order

1. Documentation and roadmap only.
2. Shared contracts/models after ownership is decided.
3. Provider/service adapters with independent tests.
4. Workflow/orchestration engine.
5. Agents, prompts, templates, memory, metrics, and observability.

## Criteria for creating `Young-Consultations/ai-sdlc`

Create the repository only after maintainers approve ownership, scope, package boundaries, independent CI, release plan, security review, and a migration plan that leaves Slugger's MVP path unchanged.
