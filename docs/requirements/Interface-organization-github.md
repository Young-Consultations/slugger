# Interface Contract — `Young-Consultations/.github` Control Plane

## Purpose and repository responsibilities

The organization repository is expected to own canonical AI-SDLC contracts, validation vocabulary, target registration, routing, compatibility, and control-plane verification. Slugger is a registered target executor and MUST NOT edit organization configuration, define a competing router, or locally fork canonical schemas.

## Required inputs to Slugger

A routed request MUST supply: canonical contract kind/version; stable task, correlation and delivery/idempotency identities; source reference and current approval context; registered target/capability; execution mode (`verify`-like non-mutating semantics or governed implementation semantics, using canonical vocabulary); bounded intent/project context; target repository/base/requested deterministic branch; draft-only policy; immutable-input identity/digest; handling/security constraints; and any contract-required retry lineage. Input may be delivered inline or by an integrity-bound artifact reference; the transport is not prescribed.

## Required outputs

Slugger SHALL return a canonical result validated by the authoritative contract, carrying all root identities and input version; observed mode/outcome; timing; evidence reference/digest; provider/gate summary appropriate to disclosure; publication mode/occurrence/reference; safe error category and retryability; and outstanding human action. Child work in future orchestration retains root correlation and produces individually valid results; aggregation MUST NOT invent status vocabulary.

## Required events and behavior

The control plane must support registration/compatibility verification, task dispatch/redelivery, contract/registry version change, and result availability. Verification dispatch SHALL cause no provider invocation, branch/commit/PR mutation, or target write. Implement dispatch remains subject to Slugger revalidation and gates. Registration does not itself approve portfolio work.

## Contract invariants

* The authoritative validator is obtained from an immutable approved contract release or equivalent trusted distribution.
* Registration identifies repository, supported contract/capability/mode, target entry point, and compatibility.
* Logical delivery identity and requested branch are stable and independent of job/run/attempt IDs.
* One canonical request has one target and draft-only publication policy for MVP.
* Routing is at-least-once; concurrency is not the deduplication guarantee.
* Contract validation occurs before Slugger run mutation.
* Canonical enums/statuses remain externally owned; Slugger supplies an adapter, not duplicate definitions.

## Failure, retry, and idempotency

Schema failure, unsupported contract, unregistered/misdirected target, unresolved dependencies, invalid executor/capability, absent stable identity, non-draft publication, or failed authority recheck MUST reject before provider execution. Redelivery uses the same logical identity. Conflicting immutable content, ambiguous ownership, or unsupported semantic version is non-retryable until governance correction. Results SHOULD be deliverable at least once and deduplicable by delivery/result identity.

## Versioning expectations

Unknown major versions fail closed. A pinned version/release is required for an execution. Contract evolution SHALL specify compatibility, deprecation period, rollout order, in-flight handling, fixtures, and downgrade/rollback behavior. Dedicated stable identity fields SHOULD replace compatibility-derived identities only through coordinated rollout. Slugger MUST NOT assume the currently documented `ai-sdlc-contract/v2` or release `ai-sdlc-v2.1.0` is permanent.

## Ownership

Organization control-plane owner: schemas, vocabularies, registry, router and compatibility verification. Slugger: supported-capability declaration, target policy, actual execution/evidence, and truthful canonical result. Portfolio owner: work and approval. Target owner: repository governance. Humans: review/merge/release.

## Assumptions, unknowns, and validation

Known context states that the organization repository has these responsibilities, but its implementation is unavailable. Validate registry enablement and authority; supported versions; validator distribution trust; artifact limits/integrity; transport authentication; redelivery/backoff/dead-letter behavior; result callback/polling mechanism; child task semantics; incident ownership; availability objectives; compatibility window; and source approval revalidation. Slugger activation SHALL remain disabled or verification-only until registry and end-to-end conformance are approved externally.
