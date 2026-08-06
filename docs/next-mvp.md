# Slugger organization next-MVP contribution

**Status:** repository planning baseline; implementation is not certified.
**External baseline:** `Young-Consultations/.github/docs/releases/next-mvp.md`, which was not inspected. This document uses the task brief as a working objective and MUST be reconciled with an immutable organization-contract release before enablement.

## Product context and release boundary

Slugger's long-term vision remains a governed software factory with reusable lifecycle capabilities, evidence, and human decision gates. Earlier v0.1.x demonstrations proved a narrower idea-to-Python-CLI workflow and real-Codex sandbox publication. Neither is the definition of this release.

For the organization next MVP, Slugger contributes only a conforming target adapter: accept one routed canonical request, make a fail-closed authorization and policy decision, execute Codex only for `implement`, validate the repository change, publish or reuse one managed draft pull request, and emit a correlated canonical result. `verify` is a non-mutating interface/conformance operation and never invokes Codex. Merge, approval of the PR, release, deployment, production operations, general multi-agent orchestration, and additional project classes are out of scope.

## Normative repository scope

The exact included Slugger requirement IDs are:

| Requirement | Next-MVP obligation |
|---|---|
| FR-INT-01 | Accept and validate the canonical request and supported contract version. |
| FR-INT-02 | Validate target identity plus stable routed authorization evidence. |
| FR-RUN-01 | Preserve task, delivery, correlation, attempt, and target identities. |
| FR-WS-01 | Confine writes and commands to the selected Slugger repository workspace and allowed paths. |
| FR-PRV-01 | Invoke Codex only for an authorized `implement` request; never for `verify`. |
| FR-VAL-01 | Apply the request/profile repository-change policy before publication. |
| FR-TST-01 | Run the bounded repository validation plan and record outcomes. |
| FR-EVD-01 | Produce safe validation and execution evidence. |
| FR-PUB-01 | Recheck gates and authorization evidence before mutation. |
| FR-PUB-02 | Publish or reuse exactly one owned open draft PR; never merge/release/deploy. |
| FR-IDM-01 | Make request handling and visible effects safe under at-least-once delivery. |
| FR-ERR-01 | Fail closed with actionable, non-sensitive error information. |
| FR-RES-01 | Map every terminal/ambiguous outcome to the externally owned canonical result. |
| FR-CNF-01 | Provide deterministic, no-Codex, no-publication contract conformance in normal CI. |

All other functional requirement IDs are deferred from this organization release: **FR-SCP-01, FR-CAT-01, FR-RUN-02, FR-PRM-01, FR-WS-02, FR-ART-01, FR-DEP-01, FR-EXE-01, FR-SMK-01, FR-REC-01, FR-GOV-01, FR-LCM-01, FR-LCM-02, and FR-EXT-01**. They remain product direction or previously demonstrated capability, not organization next-MVP exit criteria. Included requirements apply only to the routed Slugger-repository target path; they do not certify the broader factory.

## Authority and admission model

1. `portfolio-tasks` owns task approval truth. Observed transitions such as `status:approved` to `status:queued` are sibling-repository assumptions, not a locally defined protocol.
2. The organization control plane owns admission, target selection, routing, and the evidence that binds approval to an immutable task revision, target, requested mode, and delivery.
3. Slugger validates the contract-provided stable proof: issuer/authenticity, subject and revision binding, target and mode scope, authorization, issued/expiry times, freshness, and the contract-defined revocation/withdrawal check. Unavailable, stale, withdrawn, edited, malformed, contradictory, or unauthorized evidence denies execution and publication.
4. Mutable labels are not stable proof. The implementation's observed `ai-sdlc-approved` check is blueprint drift and MUST NOT be a second approval authority unless the external contract explicitly assigns that check to Slugger. A label may be informational only; a race between label reads cannot grant authority.
5. Authorization is checked before Codex and again immediately before the first target mutation. An ambiguous check fails closed. Rejection still produces/delivers a canonical result when the approved result mechanism permits it.

Exact proof representation, trusted issuer/key material, revision binding, maximum age, clock-skew allowance, revocation lookup/snapshot rules, and behavior during authority-service unavailability are external decisions and cannot be implemented from this baseline alone.

## Request processing and idempotent effects

Slugger validates the organization-owned request with its pinned validator before local mapping. It then checks the supported contract release, exact `Young-Consultations/slugger` target identity, registered capability/mode, immutable base/ref and scope, draft-only policy, identities, and repository-local allow/deny rules. Unknown required fields or semantics, unsupported versions, and malformed/cross-field-invalid requests are rejected before Codex or mutation.

The stable contract-defined delivery/publication identity and immutable-input digest—not an Actions run ID, timestamp, or mutable label—own the visible effect. On initial and pre-publication reconciliation Slugger may proceed, reuse the one structurally matching owned open draft, or block. Conflicting inputs, unowned branches, non-draft/closed/merged/wrong-base PRs, multiple matches, or indeterminate publication are preserved for reconciliation. At-least-once transport is assumed; the guarantee is idempotent effects, not exactly-once delivery.

Codex receives only the allowed repository context and an implement instruction. It has no approval, routing, publication, merge, release, or deployment authority. Candidate changes outside repository-local scope, changes to prohibited paths, secret exposure, or an incomplete/failed validation plan block publication. A successful no-change run emits the canonical no-change outcome and creates no branch or PR.

## Canonical execution result obligation

Slugger MUST use the pinned organization validator and mapping adapter rather than define a local `execution-result/v2` schema or status enumeration. It produces a canonical result for each of these observations: verify success; implement success; an existing managed draft reused; no changes required; authorization rejection; contract rejection; execution failure; validation failure; publication failure; and ambiguous or interrupted execution.

The local mapping MUST populate, where required by the external contract: contract/schema version; source task, delivery/idempotency, correlation, run and attempt identities; target repository; canonical execution status; mode and lifecycle observation; validation plan and evidence references/digests; draft PR URL/number, head/base, commit and reuse indicator when applicable; categorized safe error details; started/completed/observed timestamps; and contract-defined retryability, retry-after or human reconciliation guidance. Missing or unmappable required semantics fail conformance—Slugger must not invent a status. Result creation is durable before delivery/exposure, uses stable result identity, and is itself safe under redelivery.

The result-return mechanism is external. Until confirmed, Slugger may only describe a result port supporting the approved callback, artifact, API, event, or polling exposure. Transport acknowledgement does not change execution truth; an uncertain delivery is retried/reconciled with the same identity and payload. Logs and PR text are not substitutes for the canonical result.

## Continuous interface conformance

Normal merge-blocking CI MUST run a hermetic target-adapter suite using the immutable shared-contract fixture release and its official validator. The dependency MUST be pinned by immutable commit/release digest (not a floating branch/tag alone), with provenance and an explicit update procedure. An incompatible validator, fixture, required status, or lifecycle assertion fails the required check and blocks merge. Local fixtures may add repository-policy cases but MUST NOT copy or relax canonical schemas.

The suite uses an in-memory/local fake executor, validator adapters, fake clock/authority, fake repository, and fake publisher/result sink. It MUST prove:

- a valid `verify` request validates and returns success without mutation or executor invocation;
- a valid `implement` request invokes only the fake executor and yields a deterministic expected change or deterministic no-change outcome;
- publication is simulated, a matching managed draft is discovered and reused, and duplicate delivery has no second visible effect or executor call after completion;
- invalid target, invalid approval, withdrawn/stale approval, unsupported contract version, and malformed input are rejected before execution/mutation;
- deterministic validation failure yields a validator-accepted canonical failure result;
- all success, reuse, no-change, rejection, failure, and ambiguous/interrupted result fixtures validate against the shared release and preserve identities;
- the suite succeeds with Codex credentials unset, denies any Codex network call, and creates no real branch, commit, push, or pull request.

Tests use fixed identities, time, repository contents, executor output, validation observations, publication records, and expected canonical documents. Network is disabled or trapped. A separate credentialed end-to-end demonstration may exist but is not a normal-CI or next-MVP conformance dependency.

## Lifecycle and sequence

```text
RECEIVED -> CONTRACT_VALIDATED -> AUTHORIZED -> RECONCILED
  verify ------------------------------------------> RESULT_CREATED -> RESULT_EXPOSED
  implement -> CODEX_COMPLETED -> CHANGES_VALIDATED -> RECONCILED
                no change -------------------------> RESULT_CREATED
                publish -> DRAFT_CREATED_OR_REUSED -> RESULT_CREATED -> RESULT_EXPOSED
```

Any validation can transition to `REJECTED`; execution/validation/publication can transition to `FAILED`; interruption or an uncertain external effect transitions to `RECONCILIATION_REQUIRED`. These are local descriptive states only. The adapter maps them to the pinned external status vocabulary. No state after `DRAFT_CREATED_OR_REUSED` approves, readies, merges, releases, or deploys.

## Architecture and security boundaries

The inbound adapter authenticates the control-plane caller and invokes the external request validator. The policy/authority adapter verifies stable evidence without becoming approval owner. The coordinator holds stable identity and idempotency decisions. The Codex adapter can write only to an isolated repository workspace. The validation adapter observes the candidate with no publication credential. The GitHub adapter receives only validated files and a phase-scoped credential capable of owned branch/draft operations. The result adapter validates, stores, and delivers/exposes the canonical result. Credentials and unredacted approval material never enter Codex context, generated processes, logs, PR bodies, or safe errors.

Audit events correlate receipt, contract and authority decisions, reconciliation, executor invocation, validation, publication, result validation, and result delivery attempts. Metrics may count categorized outcomes and reconciliation backlog, but telemetry never authorizes progress and does not replace evidence.

## External validation gates

Enablement is blocked until owners of the inaccessible organization/sibling repositories confirm:

1. exact contract release, supported version string, immutable pin/digest, validator distribution and compatibility window;
2. approval-proof issuer, revision/target/mode binding, freshness, expiry, edit, withdrawal and revocation semantics;
3. canonical result schema/version, full status vocabulary and mappings for every listed outcome;
4. approved result return/exposure transport, authentication, acknowledgement, retry and reconciliation behavior;
5. Slugger target-registry entry, capability/mode declaration, base/ref/scope policy, and enablement/rollback order;
6. shared request/result/lifecycle fixtures, pinning policy, fixture update ownership, and required CI check name;
7. whether any label is contractually required at the target (none is assumed), and how observed portfolio status transitions relate to immutable authorization evidence.

Because `.github` and `portfolio-tasks` were not inspected, this document makes no cross-repository compatibility claim. Registry-disabled Slugger remains disabled even if local conformance passes.

## Repository readiness checklist

- [ ] All external gates above are resolved and recorded against immutable references.
- [ ] Every included requirement has design, interface, fixture, and acceptance-test traceability.
- [ ] Hermetic conformance passes without secrets/network/real GitHub effects and is merge-blocking.
- [ ] Authorization race, stale/edit/withdrawal, duplicate delivery, publication ambiguity, and result redelivery are exercised.
- [ ] The target allowlist/registry and least-privilege credentials are externally enabled only after conformance.
- [ ] A sandbox integration proves one validated managed draft and canonical result without enabling merge/release/deploy.
- [ ] Legacy v0.1.x certification is labeled historical and is not used as next-MVP certification.

**Readiness verdict:** documentation-ready for external contract reconciliation; **not implementation-ready or organization-enabled** until all external gates and conformance evidence are complete.
