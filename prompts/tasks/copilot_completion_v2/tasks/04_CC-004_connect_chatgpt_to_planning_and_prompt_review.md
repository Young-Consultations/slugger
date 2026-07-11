# CC-004: Connect ChatGPT to planning and prompt review

**Milestone:** M2 — Real AI agents  
**Priority:** P0  
**Implementation order:** 4  
**Depends on:** CC-002, CC-003

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

Use the ChatGPT service for requirements-oriented prompt execution and structured prompt review through the managed prompt lifecycle.

## Verified current-state problem

- ChatGPT clients and mocks exist but planning agents do not call them.
- Prompt review is not an approval input.

## Primary scope and likely files

- services/chatgpt/
- agents/planning/
- agents/support/
- prompts/templates/
- prompts/lifecycle.py
- orchestrator/context.py
- tests/test_chatgpt_service.py
- tests/test_prompt_lifecycle.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Wire planning agents to the resolved planning-generation capability.
2. Generate product vision, requirements, user stories, acceptance criteria, and project plan as validated structured artifacts.
3. Wire prompt review to the prompt registry and approval policy.
4. Add bounded retry for transient failures and explicit malformed/refused response handling.
5. Capture token usage, latency, prompt provenance, and output validation.
6. Add deterministic mocks for valid, malformed, refused, and transient-failure responses.

## Prompt-engineering requirements

- Planning prompts must cite input artifact IDs and preserve stable requirement IDs.
- Prompt-review output must contain categorized findings and confidence.
- Rule-based validation remains authoritative over model opinion.

## Software-engineering requirements

- Do not persist full sensitive prompt bodies by default.
- A failed review cannot be interpreted as approval.

## Acceptance criteria

- The project idea produces meaningful, schema-valid requirements and user stories.
- Prompt review creates structured findings and an approval recommendation.
- All behavior works with deterministic mocks and opt-in live tests.

## Required validation

- `python -m pytest tests/test_chatgpt_service.py tests/test_prompt_lifecycle.py tests/test_orchestration_pipeline.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Sample planning artifact chain
- Prompt review evidence
- Mock/live test separation

## Out of scope

- Code generation
- Canva design generation
- GitHub writes

## Rollback requirement

Switch planning capability back to the deterministic mock through configuration while retaining schema validation.

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

- Branch: `copilot/cc-004`
- Commit: `CC-004: Connect ChatGPT to planning and prompt review`
- Draft PR: `CC-004 — Connect ChatGPT to planning and prompt review`
