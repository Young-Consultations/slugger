# CC-015: Replace the eight-step placeholder recipe with the real full AI-SDLC

**Milestone:** M7 — Product workflow  
**Priority:** P0  
**Implementation order:** 15  
**Depends on:** CC-004, CC-005, CC-006, CC-010, CC-012, CC-013, CC-014

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

Create and execute a dependency-aware full-SDLC workflow from idea through approved release candidate, including design, generation, remediation, documentation, readiness, and GitHub handoff.

## Verified current-state problem

- `full-sdlc.yaml` contains eight high-level steps and omits most required stages.
- The engine can report success before validation and release evidence.

## Primary scope and likely files

- workflow/recipes/full-sdlc.yaml
- workflow/models.py
- workflow/parser.py
- workflow/graph.py
- workflow/engine.py
- workflow/escalation.py
- orchestrator/orchestrator.py
- tests/test_orchestration_pipeline.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define stages: intake, product vision, requirements, user stories, architecture, ADRs, design, design approval, implementation plan, code generation, code review/refactor, test generation, build/test, QA remediation, security remediation, documentation, traceability, readiness, release approval, GitHub handoff, release candidate, reflection.
2. Declare exact typed artifact inputs/outputs and selection rules for every step.
3. Add explicit parallelism only where artifacts are independent.
4. Add retry/escalation policies and bounded feedback loops.
5. Add environment-specific approval policies.
6. Add invalidation rules so upstream changes rerun only affected downstream steps.
7. Define terminal states: failed, cancelled, manual intervention, generated, validated, awaiting approval, production ready, released.
8. Generate a collaboration summary and project manifest.

## Prompt-engineering requirements

- Every provider-backed step references a managed prompt.
- Every step's output schema and exit criteria must be explicit.
- Reflection output cannot rewrite approved standards/prompts automatically.

## Software-engineering requirements

- No transition to production-ready without build/readiness evidence.
- Resume must preserve exact prompt/provider/artifact versions.
- No unbounded loop or hidden auto-approval.

## Acceptance criteria

- The recipe parser validates all dependencies, inputs, outputs, gates, and policies.
- A deterministic mock run executes the complete graph.
- Failure injection enters the correct remediation or terminal state.
- The old eight-step recipe is not the default full-SDLC path.

## Required validation

- `python -m pytest tests/test_orchestration_pipeline.py tests/test_task_dependencies.py tests/test_escalation.py tests/test_workflow_approval_integration.py -q`
- `python -m pytest -q`

## Pull-request evidence

- New full recipe
- Graph validation
- State/invalidation behavior
- Mock end-to-end workflow test

## Out of scope

- Live release publication
- New programming languages
- Distributed orchestration

## Rollback requirement

Keep the last validated recipe version available by version; never revert to false production success.

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

- Branch: `copilot/cc-015`
- Commit: `CC-015: Replace the eight-step placeholder recipe with the real full AI-SDLC`
- Draft PR: `CC-015 — Replace the eight-step placeholder recipe with the real full AI-SDLC`
