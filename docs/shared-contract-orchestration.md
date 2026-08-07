# Shared-contract orchestration — next-MVP target slice

[`docs/next-mvp.md`](next-mvp.md) is the normative Slugger baseline. The immutable
compatibility unit is organization release 2.2.0,
`Young-Consultations/.github@f2491872976a4dcc1633997954c03c07cbc4fced`, contract
payload `ai-sdlc-contract/v2`, and fixture manifest `TC-MVP-CI-001`.

The reusable target entry point accepts required strings `execution_input_json`
(the complete canonical execution-input object) and `concurrency_group` (transport
concurrency identity). `delivery_id`, not the concurrency group or an Actions run
ID, is the idempotency and deterministic branch identity. At-least-once retries
preserve it. A changed payload under an existing delivery ID is rejected.

Canonical task, execution-input, and execution-result schemas are consumed directly
from `contracts/task-contract.schema.json`, `contracts/execution-input.schema.json`,
and `contracts/execution-result.schema.json` at the full SHA above. No package,
floating reference, local schema, enum, fork, or compatibility-derived identity is
part of the MVP interface.

Only router-admitted canonical `approved` tasks reach target processing; `queued`
is not authorization. Slugger authenticates the caller and enforces target-local
policy but does not re-read a live source issue or require a label/second approval.
Material change creates a new `task_id` and requires new approval.

Implement mode reconciles the deterministic branch and the
`ai-sdlc-delivery-id` PR marker before mutation. It reuses one exact matching managed
draft with `duplicate-reused`, fails closed on ambiguity, and requeries after a
create race. Verify mode has no Codex, branch, or PR effect.

Slugger sends canonical results separately to
`Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@f2491872976a4dcc1633997954c03c07cbc4fced`.
That receiver is an unimplemented fail-closed skeleton, so live successful result
delivery is not currently possible. Acknowledgement is transport state, not
execution success. Slugger will not create a competing receiver.

The registry entry is disabled. Local documentation and fake-adapter implementation
may proceed, but routed execution must fail closed until organization enablement.
The fixture manifest lacks executable inputs/expected outputs for every case, so
planned CI aligns to its scenario coverage without claiming full shared-fixture
conformance or inventing organization fixtures.
