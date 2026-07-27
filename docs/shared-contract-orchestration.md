# Shared-contract orchestration

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
