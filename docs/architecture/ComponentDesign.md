# Component Design

## Component catalogue

The following logical components are mandatory responsibilities. “Owner” names the accountable role, not a source directory.

| Component | Purpose / responsibilities | Inputs → outputs | Dependencies | Lifecycle and failure | Scale / owner |
|---|---|---|---|---|---|
| Contract Boundary | Authenticate delivery; use authoritative validator; preserve canonical semantics | Envelope → validated request or rejection | Trust/config, contract distribution | Per request; unknown semantics fail before mutation | Stateless; Integration owner |
| Authority & Scope Policy | Recheck approval; target/capability fit; emit explicit scope/exclusions | Valid request + authority facts → decision/scope | Authority port, catalog | Intake and prepublication; unavailable/contradictory blocks | Cache only within freshness; Product/security |
| Capability Catalog | Declare supported/experimental/deprecated profiles and promises | Capability query → versioned profile | Approved config/artifacts | Release-versioned; missing profile unsupported | Read-heavy; Product architect |
| Identity Service | Validate/derive delivery, run, attempt, publication and digest bindings | Canonical identities/input → identity set | Digester, canonical rules | Pure; collision/conflict fatal | Horizontally safe; Domain owner |
| Run Coordinator | Persist and advance one governed state machine; deduplicate and recover | Commands/events → transitions/run views | Run store, clock, ports | Run-scoped; optimistic conflict/reconcile | Partition by delivery; Platform owner |
| Prompt & Provenance | Create reproducible bounded provider request | Intent/scope/policy → request + digest | Approved prompt assets | Per generation attempt; missing variables/version fail | CPU-light; AI product owner |
| Provider Gateway | Invoke replaceable provider under limits; normalize receipt | Request/limits → candidate receipt/error | Provider port, quota | Cancellable/time-bound; no blind retries | Separate quota pool; AI integration owner |
| Workspace Controller | Allocate contained owned workspace; mediate all candidate I/O | Run/profile → handle/inventory source | Isolation/storage | Run-scoped; ownership-proven cleanup | Workspace per run; Security/platform |
| Candidate Inventory | Normalize paths; classify/hash files; reject special/unsafe content | Workspace → protected manifest/dispositions | Content policy, digester | Re-run on mutation; limit breach fails | Stream bounded files; Security |
| Dependency Admission | Resolve declared dependencies against allow/integrity policy | Manifest/profile → acquisition plan/gate | Approved sources, policy | Before install; ambiguity/unavailability blocks | Cache verified immutable packages; Supply-chain owner |
| Isolated Verifier | Install, test, analyze, smoke with bounded resources/no publish authority | Manifest/plan/profile → observed records | Sandbox, runner | Ephemeral; timeout/crash = non-pass | Independent worker pool; Quality/security |
| Gate Engine | Evaluate completeness, pass/freshness, invalidation | Observations/bindings → gate decision | Policy, clock | On phase and before publish; no partial success | Pure/read-heavy; Domain owner |
| Evidence & Audit | Produce machine/human package; append actor/action history | Run snapshot → digest/reference/views | Evidence store, redactor | Throughout run; assembly failure blocks publish | Append/immutable storage; Assurance owner |
| Publication Controller | Preflight/reconcile target; transfer exact verified set to one owned draft | Plan/evidence → handoff record | GitHub/target adapter, gate/authority | Final bounded phase; ambiguity preserved | Serialize per publication ID; Delivery owner |
| Result & Diagnostics | Map truthful canonical result and actionable safe human output | Run/error → validated result/summary | Contract mapper/redactor | Any terminal/interim point; mapping failure retained locally | Stateless; UX/operations |
| Configuration & Secret Broker | Resolve/validate effective policy and issue phase credentials | Sources/context → config digest/secret handle | Credential authority | Startup/run phase; invalid mandatory setting fail | Stateless broker + secure authority; Security/ops |

## Standard component contract

Every component documents: stable name/version; owned decisions; accepted commands/queries; input schema and classification; output schema and provenance; pre/postconditions; idempotency; deadlines; error categories; audit events; metrics; configuration keys; secret needs; and conformance fixtures. Components communicate through typed domain records, not shared mutable dictionaries or another component’s persistence tables.

## Lifecycle interaction

Components are composed at process start, but most operations are run-scoped. Run Coordinator is the only phase-transition authority. Workspace and sandbox resources are disposable; run, audit, evidence, identity, and handoff records are durable per policy. Provider and target adapters are circuit-breakable external boundaries. Secret handles expire at phase completion.

## Failure containment

Provider failure cannot corrupt durable state or target. Sandbox failure cannot access provider/publication credentials. Evidence failure prevents publication. Publication uncertainty enters reconciliation, never regeneration or destructive repair. Optional telemetry failure never changes mandatory evidence, while mandatory local audit failure prevents consequential progression.
