# Slugger Architecture Reference

**Status:** Authoritative target architecture
**Scope:** `Young-Consultations/slugger`
**Audience:** product, architecture, engineering, assurance, operations, and AI-SDLC agents

This set defines the system Slugger **ought to be**. Authority is resolved in this order: [Vision](../VISION.md) → [Requirements](../requirements/README.md) → these architecture documents → future implementation. Current code and workflows are evidence of terminology and capabilities only. They neither enlarge supported scope nor override this design.

## Document map

| Concern | Document |
|---|---|
| Direction and system shape | [Software Architecture](SoftwareArchitecture.md), [High-Level Design](HighLevelDesign.md) |
| Internal design | [Low-Level Design](LowLevelDesign.md), [Component Design](ComponentDesign.md), [Domain Model](DomainModel.md) |
| Behavior | [Data Flow](DataFlow.md), [Sequence Diagrams](SequenceDiagrams.md), [State Models](StateModels.md) |
| Boundaries and contracts | [Interface Architecture](InterfaceArchitecture.md), [Integration Architecture](IntegrationArchitecture.md), [Repository Boundaries](RepositoryBoundaries.md) |
| Cross-cutting architecture | [Security](SecurityArchitecture.md), [Deployment](DeploymentArchitecture.md), [Observability](ObservabilityArchitecture.md), [Errors](ErrorHandling.md), [Configuration](ConfigurationArchitecture.md), [Extensions](ExtensionArchitecture.md) |
| Decisions and coverage | [ADR](ADR.md), [Traceability](ArchitectureTraceability.md) |

## Interpretation rules

1. **MUST/SHALL**, **SHOULD**, and **MAY** retain their requirements meanings. Architecture adds structure, not new product scope.
2. The supported MVP is one governed path from an approved, bounded, dependency-minimal Python CLI idea to verified evidence and at most one managed draft pull request. Full-SDLC, multi-agent, design, consulting, and other project classes remain experimental/future until promoted under BR-20.
3. “Component” means a logical responsibility, not a package, process, class, service, or deployment mandate.
4. An external repository description is a required contract and ownership boundary only. Its implementation is unknown until independently validated.
5. Generated content and human-readable external text are untrusted data. A provider claim is never a verified fact.
6. Every future change must cite requirement IDs, affected decisions/interfaces, verification, migration, and rollback. AI agents must not fill an “Unknown” with an invented assumption.

## Architecture vocabulary

The [authoritative requirements glossary](../requirements/Glossary.md) governs. Particularly important distinctions are logical delivery vs run vs attempt; candidate vs verified project; claim vs verified fact; local evidence vs optional telemetry; and draft publication vs review/merge/release/deployment.
