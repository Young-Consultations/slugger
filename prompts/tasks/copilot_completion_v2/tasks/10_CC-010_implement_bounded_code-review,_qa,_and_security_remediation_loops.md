# CC-010: Implement bounded code-review, QA, and security remediation loops

**Milestone:** M4 — Autonomous quality  
**Priority:** P0  
**Implementation order:** 10  
**Depends on:** CC-005, CC-009

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

Route structured review, test, static-analysis, and security findings back to Codex for file-scoped remediation until gates pass or an explicit escalation state is reached.

## Verified current-state problem

- Review/refactor/test/security components exist separately.
- There is no proven closed loop that changes files and reruns evidence-producing gates.

## Primary scope and likely files

- agents/development/code_review_agent.py
- agents/development/refactor_agent.py
- agents/qa/test_generator_agent.py
- agents/qa/security_review_agent.py
- workflow/escalation.py
- workflow/recipes/iterative-review-loop.yaml
- tests/test_escalation.py
- tests/test_orchestration_pipeline.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Normalize code-review, test, lint/type, dependency, and security results into one finding model.
2. Define blocking severity, affected files, requirement IDs, evidence, remediation guidance, and waiver eligibility.
3. Pass only approved findings and required file context to Codex remediation.
4. Validate changed files against an affected-file allowlist.
5. Re-materialize, rebuild, and rerun all affected gates after each attempt.
6. Set bounded attempts by finding category and escalate non-convergence.
7. Require separate human approval for any security waiver.
8. Persist every attempt, finding status, file version, and final disposition.

## Prompt-engineering requirements

- Review and remediation prompts must be separate managed prompts.
- Codex cannot mark its own blocking finding waived or resolved without new evidence.
- Summaries must include exact evidence IDs, not unsupported claims.

## Software-engineering requirements

- Retries are bounded and idempotent.
- Critical/high security findings cannot be auto-waived.
- Unrelated files may not change without explicit scope expansion.

## Acceptance criteria

- A seeded code defect is corrected and verified by rerun evidence.
- A seeded security defect is corrected or enters approval-gated waiver state.
- A non-converging fixture ends in `manual_intervention_required`, not success.
- All findings have an auditable lifecycle.

## Required validation

- `python -m pytest tests/test_escalation.py tests/test_security_scanning.py tests/test_mandatory_tests.py tests/test_orchestration_pipeline.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Unified findings
- Remediation workflows
- Attempt evidence
- Convergence/failure tests

## Out of scope

- Penetration testing
- Unlimited autonomous changes
- Auto-approval

## Rollback requirement

Restore the last passing file inventory and preserve all unresolved findings.

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

- Branch: `copilot/cc-010`
- Commit: `CC-010: Implement bounded code-review, QA, and security remediation loops`
- Draft PR: `CC-010 — Implement bounded code-review, QA, and security remediation loops`
