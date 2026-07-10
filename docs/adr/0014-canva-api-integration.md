# ADR 0014: Canva API Integration

- Status: Accepted
- Date: 2026-07-10
- Decision Makers: Slugger Engineering

## Context

Slugger is an AI Software Factory that produces complete software systems and associated engineering artifacts. Visual and design assets are a core part of many software deliverables — pitch decks, marketing materials, UI mockups, and brand assets.

Canva is a widely-used collaborative design platform that exposes a REST API (Canva Connect) for managing designs, exporting assets, and accessing brand templates. Integrating with the Canva API allows Slugger agents to programmatically create, retrieve, and export design artifacts as part of an automated SDLC workflow.

The integration must follow the same architectural patterns already established for the GitHub service:

- Interface-first design (`ICanvaService`).
- Separate concrete implementation (`CanvaClient`) from the contract.
- Mock implementation (`MockCanvaService`) for offline and test use.
- Configuration through `config/defaults.yaml` and `config/secrets.yaml` with environment-variable fallback.
- API credentials never committed to the repository.

## Decision

Add a `services/canva/` package that implements the Canva Connect REST API following the hexagonal-architecture service pattern already established in `services/github/`.

The package provides:

1. **`ICanvaService`** — abstract interface declaring the operations Slugger agents may invoke: listing designs, retrieving a single design, exporting designs, polling export jobs, listing folders, and listing brand templates.
2. **`CanvaClient`** — concrete REST implementation backed by the Canva Connect v1 API (`https://api.canva.com/rest/v1`).  The access token is sourced from `config/secrets.yaml` (`canva.access_token`) or the `CANVA_API_TOKEN` environment variable.
3. **`MockCanvaService`** — in-memory implementation used by tests and offline workflows.
4. **Domain models** — `CanvaDesign`, `CanvaExportJob`, `CanvaFolder`, `CanvaBrandTemplate`, and `CanvaExportFormat`.

Configuration is wired through:

- `config/defaults.yaml` — `canva.access_token_env` and `canva.base_url`.
- `config/secrets.yaml.example` — template showing where to place the `CANVA_API_TOKEN`.
- `config/settings.py` — `CanvaSettings` dataclass added to `Settings`.
- `config/loader.py` — `_apply_environment` resolves the env-var token; `_to_settings` populates `CanvaSettings`.

## Consequences

**Positive:**
- Slugger agents can now interact with Canva designs and exports as first-class workflow artifacts.
- The interface-first approach allows future providers (e.g. Figma, Adobe Express) to be substituted without changing agent code.
- Zero network access required for tests; `MockCanvaService` enables full offline coverage.
- Credentials follow the existing security convention — never committed, always externalized.

**Negative:**
- Canva Connect API access requires a Canva for Teams or Enterprise subscription; the free tier has limited API access.
- Export jobs are asynchronous in the real API; callers must poll `get_export_job` until status is `success`.

## Alternatives Considered

- **Embedding Canva calls directly in agents** — rejected because it violates the hexagonal-architecture boundary and makes the code untestable without network access.
- **Reusing the generic `BaseProvider` abstraction** — rejected because Canva is a design platform service rather than an AI completion/embedding provider; mixing the abstractions would reduce clarity.
