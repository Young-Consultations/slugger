# Slugger organization next-MVP target adapter

**Status:** implementation-ready interface baseline; the adapter is not implemented,
enabled, or certified. This document is authoritative for Slugger's current
organization-MVP slice. The broader product vision remains in [`VISION.md`](VISION.md).

## Immutable compatibility unit

Slugger aligns its interface to organization release **2.2.0**, contract payload
version **`ai-sdlc-contract/v2`**, and fixture set **`TC-MVP-CI-001`** at this exact
immutable reference:

```text
Young-Consultations/.github@f2491872976a4dcc1633997954c03c07cbc4fced
```

The authoritative release manifest, compatibility and release documentation,
registry, router, receiver, schemas, and fixture manifest are external facts
supplied for this alignment; they were not inspected from this repository. Slugger
therefore makes no cross-repository conformance claim.

The canonical schemas are consumed directly from these immutable files; summaries
in Slugger documentation are subordinate to them:

```text
https://raw.githubusercontent.com/Young-Consultations/.github/f2491872976a4dcc1633997954c03c07cbc4fced/contracts/task-contract.schema.json
https://raw.githubusercontent.com/Young-Consultations/.github/f2491872976a4dcc1633997954c03c07cbc4fced/contracts/execution-input.schema.json
https://raw.githubusercontent.com/Young-Consultations/.github/f2491872976a4dcc1633997954c03c07cbc4fced/contracts/execution-result.schema.json
```

There is no assumed published package, no `ai-sdlc-v2.2.0` tag, no `main`
reference, and no Slugger-owned fork, extension, enum, or replacement schema.

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

## Registry and admission

The supplied organization registry entry is:

| Field | Required value |
|---|---|
| target | `Young-Consultations/slugger` |
| enabled | `false` |
| permitted task types | `automation`, `bug-fix`, `documentation`, `feature`, `testing` |
| contract | `ai-sdlc-contract/v2` |
| draft_pr_only | `true` |
| branch_identity | `delivery_id` |
| ownership_marker | `ai-sdlc-delivery-id` |
| terminal_reuse_status | `duplicate-reused` |

The adapter **must fail closed while `enabled` is false**. Documentation alignment
and a local implementation using fakes may proceed, but live routed execution may
not. Enablement remains an organization-owned external decision.

Only canonical task status `approved` is admitted by the router. `queued` is not
authorization. Material change creates a new `task_id` and requires new approval.
The router's admitted call—not a mutable target-side label—is the organization
authorization presented to Slugger. Slugger authenticates the caller and validates
the admitted payload and local policy; it does **not** re-read the live source issue,
require `ai-sdlc-approved`, require a second approval record, or act as an approval
authority. Rich approval provenance is explicitly deferred to v3.

## Exact reusable-workflow input

The eventual reusable workflow is `.github/workflows/codex-execute.yml`. Its exact
target interface has two required string inputs:

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

## Result-receiver interface, current pin, and release transition

The release-2.2.0 baseline identifies this **current, non-live** receiver pin:

```text
Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@f2491872976a4dcc1633997954c03c07cbc4fced
```

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

The receiver at that SHA is an approved **fail-closed interface skeleton and is
not implemented**. It is suitable only for alignment and fail-closed conformance;
it is not the pin that a live-capable Slugger release will invoke. Slugger must not
create a competing receiver. Its secret is used only at the result-delivery
boundary and is not a control-plane credential. Receiver transport acknowledgement
means only that transport accepted the payload; it is not execution success and
cannot alter the canonical execution truth. Identical result redelivery must be
safe; a conflicting result under the same identity must fail closed.

Successful live result delivery becomes reachable only through a coordinated
organization release and Slugger pin update. The organization owner must first
implement and test this workflow, publish a new immutable full commit SHA containing
that implementation, and include that SHA in a new approved control-plane release.
Slugger must then replace the receiver `uses:` reference above with that new SHA,
update the documented control-plane release/SHA baseline, and pass receiver
contract, authentication, identical-redelivery, conflicting-redelivery, and failure
tests against the new revision before the registry entry may be enabled. The
implemented receiver SHA must differ from
`f2491872976a4dcc1633997954c03c07cbc4fced`; a branch, tag, or the skeleton SHA is
not an acceptable live receiver pin. Until the new full SHA is recorded here and in
the adapter workflow, successful live result delivery remains unreachable and
enablement must fail closed.

## Planned no-Codex conformance

Normal CI will use a fake executor and fake publisher, no Codex credential or
network call, and no real branch, commit, push, or PR. Planned cases align with the
authoritative `TC-MVP-CI-001` manifest scenario names and coverage:

| Area | Planned cases |
|---|---|
| happy paths | valid verify request; valid fake implement request; valid canonical result |
| admission | wrong target; disabled target; unsupported contract version; malformed input; unauthorized caller; unsupported task type; invalid `concurrency_group` |
| idempotency | duplicate delivery; changed payload under an existing delivery ID |
| publication | existing matching managed draft PR; ambiguous managed PR ownership; create-race requery; publication failure |
| execution/gates | fake Codex failure; validation failure; test failure |
| receiver/result | receiver fail-closed response; identical result redelivery; conflicting result redelivery |
| hermetic effects | no Codex network call in normal CI; no real branch; no real pull request |

The manifest is authoritative for names and coverage, but release 2.2.0 does not
provide separate executable inputs and expected outputs for every scenario.
Slugger will not invent missing organization-owned fixtures and does not claim full
shared-fixture conformance. Completion of the executable fixture release is an
external `.github` implementation dependency.

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
bounded and redacted. Changed-payload conflicts, invalid format, disabled registry,
unauthorized calls, ambiguous ownership, and receiver rejection all fail closed.

## External dependencies, limitations, and readiness

External organization-owned prerequisites are: implementation of the result
receiver followed by the coordinated release and immutable repin described above;
completion of executable fixtures/expected outputs for `TC-MVP-CI-001`; registry
enablement after local evidence; and any future publication of a package, release
artifact, or real tag (none is assumed). The immutable SHA, not a tag, is the
present dependency.

No additional Slugger-owned requirement or architecture decision is needed before
implementation. Slugger is **ready to begin local, disabled, no-Codex target-adapter
implementation** against this baseline. It is not enabled, cross-repository
conformant, or capable of successful live result delivery.
