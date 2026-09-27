# Slugger organization next-MVP target adapter

**Status:** the issue #135 recovery implementation is reviewed/merged,
immutably registered as `codex-adapter-v2.3.2` at
`797f239579bf56fbd5d11d98a1a6b5bad36d98a8`, and has complete local
zero-effect conformance evidence. Slugger remains disabled in the current
published organization 2.4.5 runtime state. No Slugger REAL execution,
Slugger-specific live receiver acceptance, or production-readiness claim is
established. This document is authoritative for Slugger's current organization-MVP
slice. The broader product vision remains in [`VISION.md`](VISION.md).

## Immutable compatibility unit

Slugger's current registered target adapter is **`codex-adapter-v2.3.2`**
at commit `797f239579bf56fbd5d11d98a1a6b5bad36d98a8`. It implements contract
payload version **`ai-sdlc-contract/v2`** and fixture set
**`TC-MVP-CI-001` v2.3.0** against the shared compatibility source:

```text
Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a
```

The historical reviewed baseline
`Young-Consultations/.github@c6090e5bbadcc2102a1cb91875466e9decdada1e`
remains unchanged. The organization source/control plane is now published as
`ai-sdlc-v2.4.5`; that does not repin this disabled target's immutable 2.3.2
adapter evidence. Mutable activation remains separate from target compatibility.

The canonical schemas and executable fixtures are organization-owned. Slugger
checks in byte-identical copies only for hermetic validation and binds their
upstream Git blob identities together with exact target files in
`config/mvp-conformance-pin.json`. Those copies and local summaries are subordinate
to the organization-owned source:

```text
contracts/task-contract.schema.json
contracts/execution-input.schema.json
contracts/execution-result.schema.json
tests/fixtures/mvp-v2/manifest.json
tests/fixtures/mvp-v2/scenarios.json
tests/fixtures/mvp-v2/expected-results.json
```

There is no assumed package, no `main` compatibility reference, and no
Slugger-owned fork, extension, enum, or replacement schema.

## Narrow responsibility and requirements

For this MVP Slugger accepts **one admitted task**, validates and executes it within
`Young-Consultations/slugger`, ends at **one validated managed draft PR** (when an
implement request produces valid changes), and sends **one canonical result**.

The exact included Slugger requirement IDs are:

| ID | MVP obligation |
|---|---|
| FR-INT-01 | Validate the complete pinned canonical request, including formats. |
| FR-INT-02 | Authenticate and authorize the admitted caller without becoming an approval authority. |
| FR-CAT-01 | Enforce the registered task-type and local-policy allowlist. |
| FR-RUN-01 | Preserve task, delivery, correlation, attempt, and target identities. |
| FR-WS-01 | Confine implement changes and commands to this repository. |
| FR-PRV-01 | Invoke Codex only after implement-mode validation and authorization. |
| FR-ART-01 | Bind validation/publication to the candidate change inventory. |
| FR-VAL-01 | Apply repository policy and required validation before publication. |
| FR-DEP-01 | Permit only dependencies needed by repository validation policy. |
| FR-EXE-01 | Execute candidate validation within the controlled boundary. |
| FR-TST-01 | Run required Slugger tests and retain the outcome. |
| FR-SMK-01 | Run any required deterministic repository smoke check. |
| FR-EVD-01 | Produce correlated, sanitized validation evidence. |
| FR-PUB-01 | Require every gate to pass before mutation. |
| FR-PUB-02 | Create or reuse at most one owned open draft PR per delivery. |
| FR-IDM-01 | Make at-least-once processing idempotent by `delivery_id`. |
| FR-ERR-01 | Fail closed with safe, actionable diagnostics. |
| FR-RES-01 | Produce and send exact canonical `execution-result/v2`. |
| FR-CNF-01 | Plan deterministic no-Codex/no-real-publication conformance CI. |

Deferred IDs are **FR-SCP-01, FR-RUN-02, FR-PRM-01, FR-WS-02, FR-REC-01,
FR-GOV-01, FR-LCM-01, FR-LCM-02, and FR-EXT-01**. Accordingly, multi-agent
orchestration, a full autonomous SDLC, cross-repository modification, automatic
merge, release, deployment, production operations, provider substitution, and rich
v3 approval provenance are future capabilities, not this MVP.

## Target capability, mutable activation, and admission

The immutable compatibility unit declares Slugger's stable target capability:

| Field | Required value |
|---|---|
| target | `Young-Consultations/slugger` |
| permitted task types | `automation`, `bug-fix`, `documentation`, `feature`, `testing` |
| contract | `ai-sdlc-contract/v2` |
| draft_pr_only | `true` |
| branch_identity | `delivery_id` |
| ownership_marker | `ai-sdlc-delivery-id` |
| terminal_reuse_status | `duplicate-reused` |

Target capability is immutable compatibility semantics; it is not current operational
activation state. Current activation is mutable organization control-plane state,
owned and enforced by the router before dispatch. Slugger does not read, pin, or
enforce historical enabled/disabled state from this compatibility revision and must
not reject a valid admitted request because this revision predates activation. This
repository does not enable Slugger; activation remains a separate organization-owned
operational decision.

Only canonical task status `approved` is admitted by the router. `queued` is not
authorization. Material change creates a new `task_id` and requires new approval.
The router's admitted call—not a mutable target-side label—is the organization
authorization presented to Slugger. Slugger authenticates the caller and validates
the admitted payload, exact target, compatibility, capability, and local policy; it
does **not** re-read the live source issue, re-evaluate activation, require
`ai-sdlc-approved`, require a second approval record, or act as an approval authority.
Rich approval provenance is explicitly deferred to v3.

## Exact target-workflow input

The target workflow is `.github/workflows/codex-execute.yml`. It exposes only
`workflow_dispatch` and has exactly two required string inputs:

| Input | Meaning |
|---|---|
| `execution_input_json` | Complete canonical `execution-input/v2` JSON object. |
| `concurrency_group` | Transport concurrency identity supplied through the organization routing path. |

`execution_input` is obsolete. The adapter does not accept an artifact alternative
as part of this interface and does not require direct sibling access, undocumented
packages/modules, control-plane credentials, a label recheck, or a second approval.
The supplied `concurrency_group` must be validated and used, but it is not the
idempotency key.

## Common target behavior

For `verify` and `implement`, the adapter shall, in order:

1. authenticate and authorize the admitted caller;
2. validate `execution_input_json` against the exact pinned execution-input schema,
   with JSON Schema **format checking** as well as structural validation;
3. require target `Young-Consultations/slugger`, contract
   `ai-sdlc-contract/v2`, an allowed task type, passing local policy, and
   `draft_pr_only: true`;
4. validate and use `concurrency_group`;
5. use `delivery_id` as the idempotency key and `correlation_id` only as the
   observability identity;
6. bind each `delivery_id` to the immutable payload digest and reject a changed
   payload under an existing delivery ID;
7. preserve the original `delivery_id` on every retry and assume at-least-once
   processing with idempotent visible effects;
8. create an exact canonical result for every accepted, rejected, blocked, or
   failed terminal path, copying input correlation ID, delivery ID, and target;
9. validate the result against the exact pinned result schema and sanitize its
   diagnostics so credentials and sensitive content cannot leak; and
10. send the result separately through the organization result receiver rather
    than return it directly to the router.

### Verify mode

Verify validates the complete request and local policy, makes no Codex call, and
creates or modifies neither branch nor PR. Success has canonical
`execution_status: verified`, with null branch and pull-request fields exactly as
required by the authoritative result schema.

### Implement mode

After all validation and authorization, implement may invoke Codex, restricted to
this repository. It derives deterministic branch identity from `delivery_id` and
searches for the `ai-sdlc-delivery-id` marker. Ambiguous ownership fails closed. A
single matching managed draft is reused with terminal status `duplicate-reused`.
Creation races are followed by a read-only requery and may converge only on that
matching managed draft. At most one managed open draft PR may exist per delivery.

Only the exact validated candidate may be published, and required Slugger
validation/tests must pass first. The adapter never operates on another repository
and never marks ready, approves, merges, releases, deploys, or performs production
operations.

## Canonical result-receiver interface

The registered 2.3.2 adapter uses the canonical receiver at:

```text
Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@ai-sdlc-v2.3.1
```

This receiver pin is part of the immutable registered target adapter. Slugger is
currently disabled, so no Slugger-specific live receiver execution/acceptance is
claimed. Receiver trusted-journal-author policy is immutable organization-owned
configuration. Slugger supplies only the narrowly scoped `CODEX_RESULT_TOKEN` at
this boundary.

| Direction | Name |
|---|---|
| input | `execution_result` |
| input | `source_issue` |
| secret | `CODEX_RESULT_TOKEN` |
| output | `accepted` |
| output | `delivery_id` |
| output | `correlation_id` |
| output | `execution_status` |
| output | `failure_category` |
| output | `diagnostic_summary` |

Slugger invokes this receiver rather than creating a competing result path. Its
secret is introduced only at the result-delivery boundary and is never available to
Codex, candidate validation, or target publication. Receiver acknowledgement means
only that transport accepted the payload; it is not execution success and cannot
alter canonical execution truth. Identical result redelivery is safe; a conflicting
result under the same identity fails closed. Receiver transport failure preserves
the already determined execution result for safe redelivery.

## No-Codex conformance

Normal CI uses a fake executor and fake publisher, no Codex credential or
network call, and no real branch, commit, push, or PR. Cases consume the executable
inputs and expected results from the authoritative `TC-MVP-CI-001` manifest scenario names and coverage:

| Area | Cases |
|---|---|
| happy paths | valid verify request; valid fake implement request; valid canonical result |
| admission | wrong target; router-side disabled-target nondispatch; unsupported contract version; malformed input; unauthorized caller; unsupported task type; invalid `concurrency_group` |
| idempotency | duplicate delivery; changed payload under an existing delivery ID |
| publication | existing matching managed draft PR; ambiguous managed PR ownership; create-race requery; publication failure |
| execution/gates | fake Codex failure; validation failure; test failure |
| receiver/result | receiver failure; identical result redelivery; conflicting result redelivery |
| hermetic effects | no Codex network call in normal CI; no real branch; no real pull request |

The compatibility unit supplies executable inputs and expected results. Slugger
consumes that oracle without redefining its schemas, status vocabulary, fixture
expectations, activation behavior, delivery/result identity, ownership semantics, or
duplicate-delivery behavior. Slugger-specific policy tests remain separate from
organization contract conformance. Normal conformance CI uses dependency-injected
fakes and makes no real Codex call, branch, commit, push, pull request, or receiver
mutation.

The checked-in report executes all 29 organization scenarios; 22 invoke the real
repository adapter seam. Every Codex, branch, commit, push, pull-request, merge,
release, deployment, production, and secret-output counter is zero. The report
does not request activation or claim production readiness.

## State, sequence, security, and failures

```text
RECEIVED -> AUTHENTICATED -> SCHEMA_VALIDATED -> POLICY_VALIDATED -> RECONCILED
  verify -> RESULT_VALIDATED -> RESULT_DELIVERY_ATTEMPTED
  implement -> FAKE/CODEX_EXECUTED -> CHANGE_VALIDATED -> DRAFT_CREATED_OR_REUSED
            -> RESULT_VALIDATED -> RESULT_DELIVERY_ATTEMPTED
```

Any rejection, block, or failure goes directly to canonical result construction
when sufficient trusted identity is available. These are local observations, not
new canonical enum values. A result-delivery failure does not rewrite the execution
outcome. Retries reuse `delivery_id`, reconcile before mutation, and never use
`correlation_id`, an Actions run ID, time, or `concurrency_group` as ownership.

Caller authentication, canonical validation, Codex, candidate validation,
publication, and result delivery are separate trust/credential phases. Codex and
candidate commands receive no publication or result token. Diagnostics are
bounded and redacted. Changed-payload conflicts, invalid format, unauthorized calls,
ambiguous ownership, and receiver rejection all fail closed.

## External dependencies, limitations, and readiness

The repository-owned adapter, immutable `codex-adapter-v2.3.2` identity,
registry tag/commit/report binding, and deterministic no-effects evidence are
complete. Slugger remains disabled. Before any future Slugger REAL execution,
organization-owned activation must deliberately enable the target and current
Slugger credential/preflight readiness plus controlled live execution/receiver
evidence must be established. Consulting-playbook's successful 2.4.5 REAL path is
not Slugger live evidence. Mutable activation remains outside this immutable unit
and outside Slugger authority; local implementation/conformance and registry
publication do not establish production readiness.
