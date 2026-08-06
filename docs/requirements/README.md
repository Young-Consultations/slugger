# Slugger Requirements Baseline

This directory is the authoritative product-requirements baseline for Slugger. It translates the product direction in [`docs/VISION.md`](../VISION.md) into verifiable, implementation-independent requirements. Where this baseline and descriptive implementation documentation differ, the vision governs product intent and this baseline governs required product behavior; neither makes an unsupported current-capability claim.

No other repository file is an authoritative Slugger product-requirements document. Experimental agents, prompts, and workflow recipes that generate requirements artifacts for generated projects are product capabilities or research inputs, not alternate specifications for Slugger. The obsolete generic requirements document template and the superseded Copilot completion requirements matrix have been removed to prevent competing baselines.

## Document set

| Document | Purpose |
| --- | --- |
| [Project requirements](ProjectRequirements.md) | Product purpose, value, scope, stakeholders, outcomes, and constraints |
| [Software requirements specification](SoftwareRequirementsSpecification.md) | Complete system-level specification and quality model |
| [Functional requirements](FunctionalRequirements.md) | Atomic capability requirements and acceptance criteria |
| [Nonfunctional requirements](NonFunctionalRequirements.md) | Measurable quality requirements |
| [Repository context](RepositoryContext.md) | Slugger ownership and system boundary |
| [Interface contracts](#interface-contracts) | Required interactions without assumptions about external implementation |
| [Use cases](UseCases.md) | Actor journeys, alternatives, and failures |
| [User stories](UserStories.md) | User-centered needs and acceptance criteria |
| [Business rules](BusinessRules.md) | Governing policies and lifecycle rules |
| [Glossary](Glossary.md) | Normative terminology |
| [Assumptions and open questions](Assumptions.md) | Confirmed facts, hypotheses, dependencies, and discovery work |
| [Traceability matrix](RequirementsTraceability.md) | Vision-to-verification coverage |

### Interface contracts

* [Portfolio intake and governance](Interface-portfolio-tasks.md)
* [Organization control plane](Interface-organization-github.md)
* [Generated-project publication target](Interface-slugger-generated-demos.md)
* [Consulting knowledge](Interface-consulting-playbook.md)
* [AI generation provider](Interface-ai-generation-provider.md)
* [GitHub platform](Interface-github-platform.md)

## Normative conventions

`MUST`, `MUST NOT`, `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are interpreted as described by RFC 2119 and RFC 8174 when capitalized. **MVP** requirements are commitments for the initial supported product boundary. **Post-MVP** requirements express the governed long-term direction and do not imply current availability. Priorities are **P0** (release-blocking), **P1** (important), **P2** (planned), and **P3** (candidate).

Each acceptance criterion has an identifier (`AC-*`) so future tests can trace to behavior without prescribing a test framework. Open items use `OQ-*`; assumptions use `CA-*` or `WA-*`; business rules use `BR-*`.

## Change governance

Changes SHALL preserve bidirectional traceability, identify affected requirements and acceptance criteria, and receive accountable human approval. A requirement is not satisfied by provider assertion alone; objective retained evidence is required. Architecture, UX, schema, API, and implementation decisions are downstream artifacts and SHALL not silently redefine this baseline.
