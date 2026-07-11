# CC-001: Correct workflow truthfulness and propagate the user idea

**Milestone:** M1 — Honest orchestration  
**Priority:** P0  
**Implementation order:** 1  
**Depends on:** None

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

Make the user's idea and project constraints authoritative workflow inputs, eliminate recursive artifact object serialization, and prevent placeholder artifact production from being reported as successful software delivery.

## Verified current-state problem

- `product_vision_agent` receives no explicit idea and emits `No explicit inputs were supplied`.
- Downstream agents embed Python artifact representations rather than typed artifact content.
- `slugger build` reports `succeeded` after producing placeholder artifacts.

## Primary scope and likely files

- models/project.py
- models/execution.py
- models/artifact.py
- workflow/executor.py
- workflow/engine.py
- orchestrator/orchestrator.py
- agents/planning/
- cli/main.py
- tests/test_orchestration_pipeline.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define a typed, immutable project brief containing idea, platform, app type, target users, constraints, nonfunctional requirements, coding-agent preference, and design preference.
2. Create one context resolver that supplies the project brief and exact typed artifact inputs to every step.
3. Replace stringification of artifact objects with explicit content/metadata serialization.
4. Validate required inputs before invoking an agent; fail with a specific missing-input error.
5. Add workflow outcome states that distinguish `artifacts_generated`, `validated`, `production_ready`, and `released`.
6. Change CLI output so a placeholder-only run cannot display production success.
7. Add regression tests using the idea `Create a simple task tracker CLI` and assert that the idea appears in requirements, architecture, and implementation context.

## Prompt-engineering requirements

- Planning prompts must receive the project brief through named variables.
- Prompts must not include dataclass repr output.
- Add fixture assertions that required idea/context variables are rendered exactly once.

## Software-engineering requirements

- Do not break resume for existing workflow records; include migration/default handling.
- Missing input must stop before agent execution.
- State changes must be persisted atomically where persistence is enabled.

## Acceptance criteria

- A full-SDLC run uses the original idea as the root of every downstream trace.
- No produced artifact contains `No explicit inputs were supplied` for a valid build request.
- No produced artifact contains nested Python object reprs.
- A placeholder-only run cannot finish in `production_ready`, `released`, or equivalent success.
- The existing 443 tests and all new tests pass.

## Required validation

- `python -m pytest tests/test_orchestration_pipeline.py tests/test_workflow_persistence.py tests/test_cli.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Before/after CLI output
- A trace showing idea → requirements → architecture input propagation
- State-transition tests

## Out of scope

- Provider integration
- File materialization
- Production build execution

## Rollback requirement

Revert the new resolver and state migration together; retain the regression tests that expose the old false-success behavior.

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

- Branch: `copilot/cc-001`
- Commit: `CC-001: Correct workflow truthfulness and propagate the user idea`
- Draft PR: `CC-001 — Correct workflow truthfulness and propagate the user idea`
