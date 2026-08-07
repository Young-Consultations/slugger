# Shared-contract orchestration

> **Next-MVP reconciliation note:** [`docs/next-mvp.md`](next-mvp.md) governs the target contribution. Exact contract release/pin, approval proof, result statuses/transport, registry enablement, and shared fixtures remain external decisions. The `ai-sdlc-v2.1.0` and `publication.identity` text below describes observed compatibility behavior only and MUST NOT be treated as the organization next-MVP selection until confirmed against an immutable baseline.

## At-least-once delivery at the Slugger target

Slugger is an idempotent consumer of organization-routed tasks. A canonical
`delivery_id` (or contract-defined `idempotency_key`) owns exactly one deterministic
`slugger/codex-delivery-*` branch and one open, managed draft pull request. The PR
body carries a machine-readable marker binding the delivery, correlation and source
issue identities, target repository, contract version, base branch, deterministic
branch, and an immutable-input digest. GitHub workflow run IDs, run attempts,
timestamps, and random values never participate in that identity.

Concurrency reduces overlapping work but is **not** the deduplication guarantee.
Every run performs a durable repository preflight before Codex. A completed owned
draft is reused without invoking Codex; an unowned branch, conflicting marker,
non-draft/closed/merged PR, wrong base, or multiple match is preserved and fails
closed for manual recovery. Branch and PR create conflicts are re-queried and may
only converge on the one structurally valid owned draft. Automation never closes
an ambiguous PR.

The organization router remains the only production dispatch authority. The
repository-local issue-label execution bridge remains retired, and publication is
always draft-only.

### Contract dependency and rollout

The next pinned organization contract must validate and preserve a stable
`delivery_id` (or `idempotency_key`) in both execution input and result, plus its
contract-defined deterministic `requested_branch`. During the coordinated rollout,
the pinned `ai-sdlc-v2.1.0` contract remains compatible: Slugger treats its existing
router-owned `publication.identity` as the delivery identity and derives the same
deterministic branch when the dedicated fields are absent. Slugger never substitutes
an Actions run ID. Rollout order is: publish and pin the new contract release; update
the organization router to emit the dedicated identity and branch; then remove this
v2 compatibility adapter after in-flight deliveries have drained.

Operators remain responsible for resolving deliberately untouched unsafe states:
multiple matching PRs, closed or merged matches, a non-draft match, a wrong-base
match, conflicting immutable input or marker data, and an existing deterministic
branch whose ownership cannot be proven. Recovery consists of inspecting and
reconciling those objects; automation does not delete branches, rewrite user work,
close PRs, or guess ownership.

Slugger's contract orchestration entry point is `ContractOrchestrator.run`. It
accepts either the canonical execution-input mapping or a canonical task mapping
(`kind="task"`). The caller must inject the validator distributed with the
organization's shared AI-SDLC contracts. Slugger intentionally ships no copied
JSON Schema, enum, approval vocabulary, executor vocabulary, task taxonomy,
priority taxonomy, failure taxonomy, or result field list.

Before creating workflow state, Slugger validates the configured contract version
and canonical payload, then fails closed unless the repository is registered,
dependencies are resolved, the canonical executor is Codex, and `draft_only` is
true. Repository registration remains caller-owned; orchestration never edits
organization configuration. Every decomposed step is another canonical execution
input. Its result is validated as a canonical execution result, retains the root
correlation and source issue, and is persisted for deterministic resume. A source
issue receives only the aggregate result, once.

The caller also supplies `is_success` from its canonical-contract adapter. Slugger
therefore sequences children without declaring its own success/status vocabulary.

## Compatibility window

Existing MVP callers may temporarily pass `idea`, `project_name`,
`github_repository`, `request_identity`, `source_issue_number`, and
`source_issue_url`. `migrate_legacy_input` translates these fields at the boundary
and emits `DeprecationWarning`. The translated input immediately joins the same
validation and production orchestration path; there is no legacy executor.

New integrations must send a canonical payload. Legacy fields are deprecated as
of Slugger 0.2 and are planned for removal in the next breaking release. Migration
should be performed upstream by replacing the legacy issue-field bridge output
with the organization router's canonical execution input. Production deployments
must inject a real Codex executor: the orchestrator has no mock or silent fallback.
