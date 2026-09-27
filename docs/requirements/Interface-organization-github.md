# Interface Contract — `Young-Consultations/.github` control plane

This interface consumes payload `ai-sdlc-contract/v2` and fixture manifest
`TC-MVP-CI-001` v2.3.0 from the shared compatibility source
`Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`.
The current organization control plane is published as `ai-sdlc-v2.4.5`, while
Slugger is registry-bound as immutable target `codex-adapter-v2.3.2` at
`797f239579bf56fbd5d11d98a1a6b5bad36d98a8` and remains disabled. See the
complete [next-MVP baseline](../next-mvp.md).

## Ownership and authority

The organization control plane owns canonical contracts, registry, admission,
routing, and result receipt. Only canonical task status `approved` is router
admissible; `queued` is not authorization, and material change requires a new
`task_id` and approval. Slugger authenticates the admitted caller and validates the
payload and local policy. It is not an approval authority and must not require or
recheck `ai-sdlc-approved`, another label, or a repository-specific approval record.
Rich approval provenance is deferred to v3.

The immutable target-capability entry targets `Young-Consultations/slugger`,
permits `automation`, `bug-fix`, `documentation`, `feature`, and `testing`, requires
`ai-sdlc-contract/v2` and `draft_pr_only: true`, and declares `delivery_id`,
`ai-sdlc-delivery-id`, and `duplicate-reused` as branch identity, ownership marker,
and terminal reuse status. Capability does not encode current activation. Mutable
enabled/disabled state is router-owned and enforced before dispatch; Slugger does
not consume or enforce historical activation state from the compatibility pin.

## Inbound target-workflow contract

`.github/workflows/codex-execute.yml` must expose only `workflow_dispatch` and
accept exactly these required strings:

* `execution_input_json`: the complete canonical `execution-input/v2` object;
* `concurrency_group`: the routing-path transport concurrency identity.

`execution_input` is obsolete. Neither an artifact alternative, a live issue-label
lookup, sibling-repository access, an undocumented module/package, nor control-plane
credentials are part of the target contract. `concurrency_group` is validated and
used, but `delivery_id` is the only idempotency key; retries retain it.

Slugger validates with format checking against the exact execution-input schema
blob at the candidate revision. It likewise consumes byte-identical pinned
task-contract, execution-result, manifest, scenario, and expected-result files.
`config/mvp-conformance-pin.json` proves their upstream identities and the exact
target implementation inputs. Slugger defines no local canonical enum, schema
fork, or extension, and assumes no published package.

## Result contract

Slugger validates canonical `execution-result/v2`, preserves the input
`delivery_id`, `correlation_id`, and target, and separately calls:

```text
Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@ai-sdlc-v2.3.1
```

That receiver pin is part of the immutable registered 2.3.2 target adapter.
Slugger is currently disabled, so no Slugger-specific REAL/live-receiver
acceptance is claimed. Trusted-journal-author policy is immutable
organization-owned configuration; Slugger passes only `CODEX_RESULT_TOKEN`.

The receiver inputs are `execution_result` and `source_issue`; its secret is
`CODEX_RESULT_TOKEN`; its outputs are `accepted`, `delivery_id`, `correlation_id`,
`execution_status`, `failure_category`, and `diagnostic_summary`. It is the
organization-owned implemented receiver for this compatibility baseline. Slugger
must not build a competing receiver. Transport acknowledgement is not execution
success, receiver credentials remain isolated to result delivery, and failed
transport preserves the immutable canonical result for safe redelivery.

## Delivery, publication, and failures

Routing is at least once. Identical redelivery converges on idempotent visible
effects; changed content under a delivery ID is rejected. `correlation_id` is for
observability only. Implement publication is limited to one managed open draft per
delivery in this repository. Ownership ambiguity fails closed, matching work is
reused, and a create race is requeried. Verify makes no Codex call or mutation and
returns canonical `verified` with schema-required null publication fields.

Every accepted, rejected, blocked, or failed terminal path produces a sanitized
canonical result when trusted identity is available. Identical result redelivery is
safe; conflicting redelivery fails closed. No target operation merges, releases,
deploys, performs production operations, or touches another repository.

## Version, activation, and conformance

All shared schema/fixture identities use the full candidate SHA and exact Git blob
IDs; `main`, a mutable compatibility reference, and an assumed package are
prohibited dependencies. `TC-MVP-CI-001` supplies executable inputs and expected
results and remains the semantic oracle; Slugger-specific tests may extend local
policy coverage but cannot redefine organization expectations. The checked-in
report passes 29/29 scenarios through the pinned adapter/harness, with 22 adapter
invocations and all ten prohibited-effect counters at zero. Passing conformance
does not enable Slugger: mutable activation remains exclusively owned by the
organization router.
