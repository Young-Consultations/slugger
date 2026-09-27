# Integration Architecture

> **Next-MVP integration slice:** authenticated `execution_input_json` plus
> `concurrency_group` → local policy/Codex/validation → managed Slugger draft →
> canonical result through the receiver pin captured by immutable registered
> target `codex-adapter-v2.3.2`. Exact shared schema/fixture blobs remain pinned
> at `e27b8a5`; the organization control plane is published at 2.4.5 and mutable
> activation remains router-owned. Slugger is currently disabled and has no
> Slugger-specific live-execution/receiver acceptance. See
> [`docs/next-mvp.md`](../next-mvp.md).

## Classification convention

**Known** is stated by Vision/Requirements or observable within this repository. **Assumed** is a design precondition needing owner validation. **Unknown** must block dependent production reliance; it is never filled from another repository’s presumed implementation.

## Integration register

| Integration | Known | Assumed | Unknown / validation required |
|---|---|---|---|
| `portfolio-tasks` | Owns structured intake, backlog, priority, approval/withdrawal; context arrives via control plane. | Stable task/revision and attributable approval can be referenced. | Approval expiry/change semantics, fields, SLA, auth, notifications, retention. |
| Organization `.github` | Published control plane is `ai-sdlc-v2.4.5`; shared v2 schemas/fixtures remain sourced from `e27b8a541afbd27b4be5606a19ffa43637ad312a`; Slugger is registry-bound as `codex-adapter-v2.3.2` at `797f239579bf56fbd5d11d98a1a6b5bad36d98a8` with passing conformance and is disabled. | Authenticated at-least-once delivery uses the documented inputs and stable identities when the router admits an enabled target. | Slugger-specific current credential/preflight readiness, deliberate activation, controlled live execution/receiver proof, backoff/dead-letter policy, and outage operations. |
| AI provider | Produces untrusted candidates through replaceable bounded contract. | Cancellation, limits, receipt/error/usage metadata are available or emulated safely. | Model guarantees, retention/training, regional handling, exact idempotency, rate/SLA, data rights. |
| GitHub platform | Current system of record and draft publication platform. | Least-privilege branch/PR operations and observable reconciliation are possible. | Token model/lifetime, protection/rate limits, outage objectives, checks/forks, API evolution. |
| Target repository (`slugger-generated-demos` named sandbox) | Separate target; owns base, policy, review/merge. Slugger only owns proven managed branch/draft. | Approved target permits generated draft content. | CODEOWNERS/base/protection/license/retention/cleanup/automation/reviewer SLA. |
| Dependency sources | Controlled acquisition is required. | Immutable integrity-qualified packages can be made available. | Approved sources, lock policy, license/signature/SBOM requirements, outage and revocation. |
| Isolation/runtime | Generated behavior must run in controlled isolation without publication authority. | Deployment can prove filesystem/process/network/resource/credential controls. | Approved technology/control strength, tenancy, egress policy, cleanup assurance, platform availability. |
| Credential authority | Secrets phase-scoped, auditable and absent from generated runtime. | Short-lived/least-privilege credentials can be issued. | Broker technology, TTL, rotation, incident/revocation, workload identity. |
| `consulting-playbook` (future) | Owns consulting truth; not required for MVP. | Knowledge could be consumed only as versioned governed input. | Contract, provenance, rights, classification, structure, refresh and conflict policy. |

## Interaction patterns

* **Request/result:** asynchronous-at-least-once is the safe baseline; a synchronous adapter may wait but does not change lifecycle semantics.
* **Provider and target:** command/response with deadline plus durable operation identity and later reconciliation.
* **Events:** conceptual facts may be transported by webhook, queue, workflow, or polling; architecture requires identity, authenticity, ordering/revision semantics and deduplication, not a technology.
* **Artifacts:** use immutable digest-bound references where inline limits are exceeded; retrieval must authenticate, authorize, verify integrity and classification.
* **Synchronization:** Slugger returns results; it never directly synchronizes portfolio lifecycle. External owners decide how their state changes.

## Workflow boundaries

Verification-only requests validate contract, registration and wiring without provider invocation or target mutation. Implementation requests remain subject to authority/scope/preflight and all gates. Draft availability is a handoff event, not completion of portfolio work. Human merge/release/deployment occurs entirely outside Slugger.

## Resilience expectations

Use timeouts, quotas, circuit breakers and bounded jittered retry for transient boundaries. Persist enough intent to reconcile ambiguous completion. Backpressure before generation when verifier/publication capacity is unavailable. Do not retry invalid contracts, withdrawn authority, policy denials, integrity mismatches, or ambiguous ownership. External outage retains evidence and returns a safe actionable result.

## Change management

Each integration has an accountable owner, contract version, conformance fixtures, compatibility matrix, threat review, rollout order, canary/verification mode, rollback and in-flight policy. No integration graduates from Unknown/Assumed to production Known without retained evidence and owner approval.
