# CC-012: Fix human approval persistence, quorum, CLI decisions, and resume security

**Milestone:** M5 — Auditability  
**Priority:** P0  
**Implementation order:** 12  
**Depends on:** CC-011

## Copilot Agent assignment

Act as both:
- a senior Python software engineer responsible for executable, secure, maintainable behavior; and
- a senior prompt engineer responsible for versioned, testable, structured AI instructions.

Complete this task in one focused draft pull request.

## Read first

- `prompts/tasks/copilot_completion_v2/MASTER_COPILOT_AGENT_PROMPT.md`
- `prompts/tasks/copilot_completion_v2/OFFICIAL_INTEGRATION_REFERENCES.md` when external services are involved
- Applicable system prompts and ADRs
- Current source and tests named in this task

## Objective

Make approvals durable, version-bound, auditable, quorum-aware, and impossible to bypass during restart or resume.

## Verified current-state problem

- Approval policy and record IDs are not fully persisted.
- Resume can execute a protected step after approval state is lost.
- Quorum is stored but not enforced; CLI cannot approve/reject.

## Primary scope and likely files

- workflow/approvals.py
- workflow/persistence.py
- workflow/engine.py
- workflow/models.py
- cli/main.py
- models/artifact_lineage.py
- tests/test_approval_gates.py
- tests/test_workflow_approval_integration.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Persist approval policy, pending record, decisions, comments, quorum, expiration, and audit events.
2. Bind each request and decision to exact artifact versions, checksums, readiness policy version, and workflow transition.
3. Implement authorized role/quorum evaluation.
4. Invalidate approval when a protected artifact or mandatory evidence changes.
5. Implement CLI list/show/approve/reject commands with stable JSON and mandatory rationale.
6. Resume by loading and validating the existing decision; never create or bypass a new gate silently.
7. Use append-only audit events with integrity checks.
8. Add process-restart, stale artifact, duplicate decision, unauthorized actor, quorum, expiry, rejection-to-rework, and bypass regression tests.

## Prompt-engineering requirements

- Approval summaries must be generated from immutable evidence.
- The model cannot approve its own prompt, finding waiver, or release.

## Software-engineering requirements

- Production release approval cannot be disabled by generated project content.
- No protected transition executes without a valid decision.
- Authentication tokens are never stored in audit records.

## Acceptance criteria

- The previously reproduced resume bypass is impossible.
- Approvals survive process restart.
- Quorum and role policy are enforced.
- CLI decisions are auditable and tied to exact evidence.

## Required validation

- `python -m pytest tests/test_approval_gates.py tests/test_workflow_approval_integration.py tests/test_workflow_persistence.py tests/test_cli.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Durable approvals
- CLI
- Audit trail
- Security regression tests

## Out of scope

- SSO/identity provider
- Email/Slack notifications
- Web UI

## Rollback requirement

Pause all protected workflows in `manual_intervention_required`; do not fall back to auto-approval.

## Definition of Done

This task is done only when:

1. Every acceptance criterion has objective evidence in the draft pull request.
2. Every required validation command passes or an explicitly approved platform limitation is documented.
3. The complete repository test suite passes.
4. New behavior is exercised through the primary orchestration path, not only through isolated unit tests.
5. Documentation, configuration examples, prompt metadata, and migrations are updated.
6. No secret, credential, private token, or sensitive generated content appears in committed files or logs.
7. The task has not introduced a duplicate subsystem or an unbounded retry/agent loop.
8. The pull request remains draft until human review is complete.

## Git guidance

- Branch: `copilot/cc-012`
- Commit: `CC-012: Fix human approval persistence, quorum, CLI decisions, and resume security`
- Draft PR: `CC-012 — Fix human approval persistence, quorum, CLI decisions, and resume security`
