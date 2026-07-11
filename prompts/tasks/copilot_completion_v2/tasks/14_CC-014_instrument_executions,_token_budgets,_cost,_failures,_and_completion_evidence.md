# CC-014: Instrument executions, token budgets, cost, failures, and completion evidence

**Milestone:** M6 — Governed intelligence  
**Priority:** P1  
**Implementation order:** 14  
**Depends on:** CC-003, CC-011

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

Connect existing telemetry, cost, token-budget, and failure analytics to every run, step, agent, provider call, artifact publication, approval, quality gate, and release decision.

## Verified current-state problem

- Observability components exist but primary execution instrumentation is incomplete.
- Completion percentages have previously been qualitative.

## Primary scope and likely files

- observability/
- workflow/engine.py
- workflow/executor.py
- agents/base.py
- providers/
- services/
- config/settings.py
- tests/test_telemetry.py
- tests/test_cost_tracking.py
- tests/test_acceptance_metrics.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define versioned correlated events with run, step, attempt, agent, provider, prompt, and artifact IDs.
2. Instrument lifecycle transitions, provider calls, retries, fallbacks, approvals, gates, and release actions.
3. Extract provider usage and distinguish actual from estimated cost.
4. Enforce soft/hard budgets by run, phase, agent, and provider.
5. Normalize failures and correlate remediation outcome.
6. Calculate completion from the requirements/evidence matrix, not agent self-report.
7. Add CLI/report exports for status, blockers, cost, failures, and completion.
8. Apply field-level redaction, payload limits, retention, and failure isolation.

## Prompt-engineering requirements

- Record prompt ID/version/hash, not raw sensitive prompts by default.
- Prompt effectiveness metrics must remain advisory and traceable.

## Software-engineering requirements

- Telemetry failure cannot corrupt workflow state.
- Retries and resumes must not double-count.
- Seeded secrets must never appear in persisted output.

## Acceptance criteria

- Every execution path emits a complete correlated event chain.
- Budgets block or escalate before overrun.
- Completion is evidence-backed.
- Redaction/leak tests pass.

## Required validation

- `python -m pytest tests/test_telemetry.py tests/test_cost_tracking.py tests/test_token_budgeting.py tests/test_acceptance_metrics.py tests/test_observability_dashboard.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Instrumentation
- Budget enforcement
- Completion metric
- Operational reports
- Redaction tests

## Out of scope

- External SIEM
- Billing settlement
- Predictive analytics

## Rollback requirement

Disable noncritical exporters while retaining local redacted audit events and hard budget checks.

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

- Branch: `copilot/cc-014`
- Commit: `CC-014: Instrument executions, token budgets, cost, failures, and completion evidence`
- Draft PR: `CC-014 — Instrument executions, token budgets, cost, failures, and completion evidence`
