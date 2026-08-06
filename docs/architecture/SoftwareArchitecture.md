# Software Architecture Overview

## Executive summary

Slugger is a governed AI Software Factory. It consumes complete approved intent, determines whether a declared capability is supported, establishes durable identity, obtains untrusted candidate content through a replaceable provider, verifies it in controlled isolation, produces integrity-bound evidence, and may hand the exact verified inventory to a demonstrably owned draft review. Humans and external governance retain approval, architecture judgment, merge, release, deployment, and production authority.

The target architecture is a modular monolith by default, organized as a clean/hexagonal system with a deterministic application pipeline, domain policy at its center, and replaceable adapters at trust boundaries. Logical components may later separate only when measured scale, isolation, or availability needs justify the operational cost.

## Architectural vision and goals

| Goal | Architectural response |
|---|---|
| Governed transformation | One policy-controlled application pipeline; no adapter can skip a gate. |
| Traceability | Immutable identities, append-only transition history, manifests, evidence digests, and provenance throughout. |
| Human authority | Approval is externally attributed and revalidated; automation ends at draft handoff. |
| Safety | Treat candidates as hostile; separate credentials; validate before controlled execution; fail closed. |
| Reliable recovery | Durable phase boundaries, leases/ownership, idempotency, bounded retry, evidence invalidation. |
| Composable evolution | Capability profiles, ports, versioned contracts, conformance suites, and promotion gates. |
| Organizational separation | No shared database/source coupling; canonical request/result boundary; attributed external facts. |

## Design principles

* **Policy before mechanism:** domain decisions precede provider, filesystem, process, or GitHub actions.
* **Functional core, imperative shell:** deterministic validation/decision logic surrounds explicitly recorded side effects.
* **Ports and adapters:** application/domain code depends on owned ports; infrastructure implements them.
* **One supported path:** all entry points normalize into the same use cases and gates (BR-25).
* **Artifact- and evidence-first:** outputs are immutable/integrity-addressed observations, not log-derived claims.
* **Least authority by phase:** generation, verification, and publication never share unnecessary credentials.
* **Truthful uncertainty:** failed, skipped, stale, unknown, and residual-human-decision never collapse into pass.
* **AI-agent legibility:** stable IDs, schemas, machine-readable outcomes, explicit invariants, and small bounded tasks.

## Guiding constraints

GitHub is the organizational system of record and current publication platform. Python CLI is the only committed MVP project class. Provider output is nondeterministic and untrusted. Cross-repository delivery is at least once and may be concurrent. External repository implementations and SLAs are unavailable. Supported execution must remain independent of experimental packages. A credentialed environment and controlled execution substrate are required, but no infrastructure product is prescribed.

## Quality attributes

| Attribute | Design tactic / acceptance direction |
|---|---|
| Security | Deny-by-default policies, phase isolation, content inventory, secret scanning/redaction, least privilege, no generated access to publication credentials. |
| Reliability | Atomic durable transitions, idempotent ownership, checksums, leases, bounded retry, last-known-good resume. |
| Auditability | Correlation on every record; actor/time/reason; tamper evidence; attributed external snapshots. |
| Maintainability | Dependency rule, cohesive capabilities, contract tests, no experimental imports in supported core. |
| Testability | Pure policy services, fake ports, golden fixtures, fault injection at every phase boundary. |
| Scalability | Independent run workers, keyed serialization by delivery, quotas/backpressure, stateless interface adapters. |
| Performance | Preflight before expensive generation; reuse exact completed delivery; stream/hash bounded artifacts. |
| Usability | Human and machine summaries state outcome, checks, limitations, recovery, and required action. |
| Portability | Logical ports avoid vendor behavior except the declared GitHub constraint; controlled runtime is replaceable. |
| Observability | Structured events, metrics and traces without confusing optional telemetry with required evidence. |

## Architectural style

The architecture combines clean architecture, hexagonal ports/adapters, domain modeling, and a persisted process manager. The domain contains identities, invariants, policies, and lifecycle rules. Application use cases orchestrate phases. Inbound adapters translate CLI/automation/canonical contracts. Outbound adapters access authority verification, provider execution, storage, containment, dependency sources, time, and publication. Dependency direction always points inward.

## System and repository responsibilities

Slugger owns supported capability declaration, request enforcement, run/delivery correlation, workspaces, provider request provenance, inventory, validation, controlled verification, evidence, retry/resume, and bounded draft publication. It does not own portfolio intent/priority/approval, organization contracts/routing, provider behavior, GitHub behavior, target governance, review/merge/release/deployment, generated-product operations, or consulting truth. See [Repository Boundaries](RepositoryBoundaries.md).

## Major components

1. Interface adapters and canonical contract adapter.
2. Intake, authority, scope, and capability policy.
3. Run coordinator and durable lifecycle repository.
4. Prompt/provenance assembler and provider gateway.
5. Workspace/containment and candidate inventory.
6. Static validation, dependency admission, and isolated verifier.
7. Evidence assembler and audit journal.
8. Publication policy and target adapter.
9. Configuration, secrets, diagnostics, and optional extension governance.

## Architectural decisions

The binding decision set is maintained in [ADR.md](ADR.md): single governed pipeline; clean dependency direction; persisted process manager; untrusted candidate boundary; capability profiles; integrity-bound evidence; idempotent draft handoff; separated phase authority; explicit contract/version adapters; and experimental isolation.

## Risks and mitigations

| Risk | Exposure | Architectural mitigation |
|---|---|---|
| Prompt injection / malicious output | Generated execution or publication | Treat text as data; inventory and policy before execution; sandbox; exact allowlisted publication. |
| Contract drift | Wrong authorization/status | Trusted validator, pinned compatible versions, unknown major fail closed, fixtures. |
| Duplicate/racing delivery | Cost or multiple PRs | Durable key ownership, leases, compare-and-set, structural target reconciliation. |
| Stale evidence | Unsafe publication | Bind evidence to immutable input, candidate, policy, config, tool and environment digests. |
| Credential leakage | Cross-boundary compromise | Brokered phase-scoped secrets; redaction/canaries; generated runtime has none. |
| External outage/ambiguity | Partial state | Categorized retry, checkpoint, no guessing/destructive cleanup, actionable blocked result. |
| Overstated readiness | Human misdecision | Scoped claims and residual risks; never call MVP output production-ready. |
| Experimental coupling | Unsupported behavior becomes required | Build-time dependency rules and separate registration/runtime paths. |

## Technical debt assessment

The current repository visibly contains both an MVP execution path and broad experimental subsystems, multiple orchestration/state/artifact abstractions, and workflow-level business behavior. These are migration signals, not target decisions. Highest-priority debt is architectural duplication and unclear authority across workflows versus product core; followed by contract/schema duplication risk, fragmented persistence/evidence, infrastructure-aware orchestration, and documentation that historically described implementation states. A future implementation should inventory each existing capability as **retain behind port**, **migrate**, **experimental quarantine**, or **remove**; no behavior is promoted merely because tests exist.

## Future evolution strategy

1. Freeze the supported capability catalog and conformance fixtures.
2. Establish domain/application boundaries and one canonical pipeline behind existing entry points.
3. Migrate durable identities, state, evidence, and publication ownership with reconciliation tooling.
4. Quarantine or extract experimental functionality without making the MVP depend on it.
5. Promote each new project class/provider/phase only with BR-20 evidence, threat analysis, contracts, owner, human gate, compatibility and rollback.
6. Split deployment units only for demonstrated contention, privilege isolation, or availability—not package aesthetics.
