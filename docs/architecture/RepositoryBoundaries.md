# Repository Boundaries

## Owned by this repository

* Slugger product vision, requirements, architecture, supported capability catalog, generation/verification policy, and release conformance.
* Validation of complete approved input at its boundary and truthful rejection/status.
* Delivery/run/attempt/publication identities as defined within canonical constraints; durable state and recovery.
* Provider request construction/provenance and constrained invocation.
* Run-owned isolated workspaces; generated candidate inventory, policy disposition and integrity.
* Observed static, dependency, install, test, security and smoke checks within declared scope.
* Correlated evidence, audit history, safe diagnostics and result mapping.
* Idempotent preflight and mutation of only a demonstrably owned deterministic branch/open draft.
* Supported/experimental separation, vulnerability response, migration/deprecation and interface conformance.

## Explicitly not owned

| Concern | Owner | Slugger responsibility only |
|---|---|---|
| Work intent, backlog, priority, approval/withdrawal | Portfolio authority/accountable humans | Consume, attribute, revalidate; never edit/infer. |
| Canonical organization schema/vocabulary, registry, routing | Organization control plane | Adapt/validate/return conformance result; never fork. |
| Provider model/algorithm and claim truth | AI provider | Bound request, distrust response, observe metadata. |
| GitHub service behavior | GitHub | Use least privilege, reconcile, fail safely. |
| Target base, protection, user files, review and merge | Target owner/humans | Preflight and mutate exact proven managed draft only. |
| Dependency package truth/source operations | Dependency source/owners | Admit against policy and record provenance/integrity. |
| Generated product release, deployment, production and support | Target product owners | State limitations and provide review evidence. |
| Consulting methods/knowledge truth | `consulting-playbook` owner | Optional future versioned consumption only. |
| Infrastructure product selection/operation | Deployment operator | Specify required controls and expose health/evidence. |

## Expected collaborators

Product owner and architects govern supported profiles; security owns threat/control and exception review; quality owns verifier/conformance evidence; platform/operations provide isolation, durability, credentials and observability; external repository owners govern their contracts; accountable humans review consequential decisions. Collaboration is through explicit contracts, not source imports or shared databases.

## Data ownership

| Data | Authority / lifecycle |
|---|---|
| Canonical request fields/status vocabulary | External owner; Slugger stores attributed validated snapshot/ref. |
| Approval/priority/source task | Portfolio owner; Slugger stores proof/reference and observation time. |
| Run state/config/policy/provenance/observations | Slugger; retained/exported/deleted by classification policy. |
| Candidate before handoff | Slugger run boundary; untrusted, contained, cleaned only by ownership proof. |
| Manifest/evidence/audit | Slugger; immutable/integrity-protected and access controlled. |
| Branch/commit/PR after publication | Target/GitHub authoritative; Slugger retains correlated observation/digest. |
| Secrets | Credential authority; Slugger receives ephemeral handles, never ownership. |
| Optional telemetry | Operator under declared policy; cannot replace run evidence. |

## Lifecycle ownership

Slugger owns acceptance through terminal run/result and draft handoff record. External governance owns pre-acceptance approval and post-result portfolio decisions. Target humans own review onward. Cleanup of Slugger resources is Slugger’s auditable responsibility; target cleanup is target-owned unless a separately approved, structurally safe contract exists. Experimental promotion requires product, architecture, security, quality and human approval before it can enter supported lifecycle.

## Boundary enforcement tests

Future builds must verify dependency direction, absence of supported-to-experimental imports, canonical fixtures without external repositories present, no source repository mutation, no generated access to credentials/Slugger source, exact publication inventory, and no automated merge/release/deploy operation.
