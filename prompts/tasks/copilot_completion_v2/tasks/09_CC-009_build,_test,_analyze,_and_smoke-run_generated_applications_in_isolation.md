# CC-009: Build, test, analyze, and smoke-run generated applications in isolation

**Milestone:** M3 — Runnable output  
**Priority:** P0  
**Implementation order:** 9  
**Depends on:** CC-008

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

Create an isolated build runner that installs the generated project, compiles/imports it, runs tests, measures coverage, performs static/security/dependency checks, and runs a template-specific smoke test.

## Verified current-state problem

- `TestRunnerAgent` formats context into Markdown and executes nothing.
- Standalone validators exist but are not connected to generated workspaces.

## Primary scope and likely files

- agents/qa/test_runner_agent.py
- validators/test_gate.py
- validators/security_scanner.py
- validators/readiness.py
- services/dependency_checker.py
- services/build_runner.py
- config/settings.py
- tests/test_mandatory_tests.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define build plan, phase result, command evidence, and complete build result models.
2. Implement a temporary virtual-environment runner; add an optional container adapter.
3. Allow only template-declared commands and sanitize environment variables.
4. Run dependency installation, compile/import, formatter/linter check, type check, unit tests, integration tests, coverage, security scan, dependency audit, and smoke command.
5. Disable network by default and require explicit policy for tests needing it.
6. Bound runtime, memory where available, process count, and captured output.
7. Persist reports and logs as evidence artifacts tied to the file inventory hash.
8. Replace `TestRunnerAgent` placeholder output with runner execution.

## Prompt-engineering requirements

- No provider prompt may claim a check passed; only command/tool evidence can pass a gate.
- Failure summaries passed to remediation prompts must be bounded, structured, and redacted.

## Software-engineering requirements

- Generated commands cannot modify the host repository.
- Host secrets cannot enter the generated process environment.
- Tool unavailable in production mode is a failed gate.

## Acceptance criteria

- A generated CLI fixture installs, tests, and smoke-runs successfully.
- An intentionally broken fixture fails with structured evidence.
- Coverage/static/security/dependency results are machine-readable.
- The workflow cannot advance to readiness when a mandatory build phase fails.

## Required validation

- `python -m pytest tests/test_mandatory_tests.py tests/test_security_scanning.py tests/test_dependency_updates.py tests/test_build_runner.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Build runner
- Isolation policy
- Evidence models
- Success/failure fixtures

## Out of scope

- Production deployment
- Unrestricted shell execution
- Performance/load testing

## Rollback requirement

Disable execution and leave the workspace in `generated_not_validated`; do not mark it successful.

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

- Branch: `copilot/cc-009`
- Commit: `CC-009: Build, test, analyze, and smoke-run generated applications in isolation`
- Draft PR: `CC-009 — Build, test, analyze, and smoke-run generated applications in isolation`
