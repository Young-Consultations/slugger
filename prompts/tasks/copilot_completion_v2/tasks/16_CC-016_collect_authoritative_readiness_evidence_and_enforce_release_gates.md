# CC-016: Collect authoritative readiness evidence and enforce release gates

**Milestone:** M7 — Product workflow  
**Priority:** P0  
**Implementation order:** 16  
**Depends on:** CC-009, CC-010, CC-011, CC-012, CC-015

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

Build the readiness decision from authoritative persisted evidence and make it impossible to create a release candidate when any mandatory gate or approval is missing.

## Verified current-state problem

- `ProductionReadinessEngine` is standalone and receives manually supplied values.
- Release and deployment agents do not enforce it.

## Primary scope and likely files

- validators/readiness.py
- validators/quality_gate.py
- agents/operations/release_agent.py
- agents/operations/deployment_agent.py
- models/manifest.py
- workflow/recipes/full-sdlc.yaml
- tests/test_readiness_engine.py
- tests/test_release_automation.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Create an evidence collector for exact workspace/file inventory, build, tests, coverage, static analysis, security, dependencies, docs, standards, traceability, approvals, provider health, and budget status.
2. Version the readiness policy and mandatory gate set.
3. Separate readiness score from mandatory gates; a high score cannot override a failure.
4. Generate JSON and Markdown reports with evidence IDs and remediation actions.
5. Hash/freeze the candidate and invalidate readiness on any artifact change.
6. Define recommendations: blocked, remediation required, approval required, release candidate, production ready.
7. Enforce the result in release/deployment agents and workflow transitions.

## Prompt-engineering requirements

- Readiness narrative must be generated from structured evidence.
- No model may fabricate missing test, security, approval, or deployment evidence.

## Software-engineering requirements

- Critical/high unresolved security findings block release.
- Missing tool execution is not a pass.
- Final release approval is bound to the frozen candidate.

## Acceptance criteria

- A broken fixture is blocked with exact failed gates.
- An unchanged passing fixture reaches release-candidate state.
- Changing one file invalidates readiness and approval.
- Release/deployment cannot bypass the collector.

## Required validation

- `python -m pytest tests/test_readiness_engine.py tests/test_release_automation.py tests/test_project_manifest.py tests/test_approval_gates.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Evidence collector
- Versioned policy
- Reports
- Release enforcement
- Invalidation tests

## Out of scope

- Business KPI scoring
- Production credentials
- External certification

## Rollback requirement

Invalidate the candidate and return to `validated_not_ready`; preserve all evidence.

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

- Branch: `copilot/cc-016`
- Commit: `CC-016: Collect authoritative readiness evidence and enforce release gates`
- Draft PR: `CC-016 — Collect authoritative readiness evidence and enforce release gates`
