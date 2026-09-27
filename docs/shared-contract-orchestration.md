# Shared-contract orchestration — next-MVP target slice

[`docs/next-mvp.md`](next-mvp.md) is the normative Slugger baseline. Slugger
consumes shared compatibility source
`Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`,
contract payload `ai-sdlc-contract/v2`, and executable fixture oracle
`TC-MVP-CI-001` v2.3.0. The current registered target is
`codex-adapter-v2.3.2` at `797f239579bf56fbd5d11d98a1a6b5bad36d98a8`;
the organization control plane is published at 2.4.5 and Slugger remains disabled.
Historical baseline `c6090e5bbadcc2102a1cb91875466e9decdada1e` is unchanged.

The reusable target entry point accepts required strings `execution_input_json`
(the complete canonical execution-input object) and `concurrency_group` (transport
concurrency identity). `delivery_id`, not the concurrency group or an Actions run
ID, is the idempotency and deterministic ownership identity. At-least-once retries
preserve it. A changed payload under an existing delivery ID is rejected.

Canonical task, execution-input, and execution-result schemas plus all three shared
fixture files are checked in byte-identically for hermetic validation. Their exact
upstream Git blob identities and the exact target wrapper/adapter/test files are
bound by `config/mvp-conformance-pin.json`. No package, floating reference, local
schema semantics, enum, fork, or compatibility-derived activation state is part of
the MVP target interface.

Immutable compatibility defines protocol and target-capability semantics. Mutable
activation is separate organization control-plane state enforced by the router
before dispatch. Slugger authenticates the admitted caller and enforces exact
target, contract, schema/format, task type, mode, draft-only, delivery, ownership,
and repository-local policy, but it neither reads historical enabled state nor
rechecks a live source label or approval.

Implement mode reconciles the deterministic delivery branch and organization-owned
PR marker before mutation. It reuses one exact matching managed draft, fails closed
on ambiguity, and requeries after a create race. Verify mode has no Codex, branch,
PR, or publication effect.

Slugger sends canonical results separately to
`Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@ai-sdlc-v2.3.1`.
That exact receiver pin is part of immutable target evidence. Slugger has no
current live execution/receiver acceptance because the target remains disabled.
Receiver trust policy remains organization-owned; the target supplies only
`CODEX_RESULT_TOKEN`.
Acknowledgement is transport state, not execution success. Result credentials are
isolated from Codex and target publication; identical redelivery is safe and a
conflicting result fails closed. Slugger does not create a competing receiver.

`TC-MVP-CI-001` supplies executable inputs and expected results. Slugger consumes
that oracle without redefining its semantics and keeps genuinely local target-policy
tests separate. Normal conformance CI injects fakes and makes no real Codex call,
branch, commit, push, pull request, or receiver mutation. Passing local conformance
does not activate the target. The checked-in report passes all 29 scenarios, invokes
the real adapter seam in 22, and records zero for all ten prohibited-effect counters.
