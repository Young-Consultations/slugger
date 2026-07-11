# CC-002: Create managed prompts and structured artifact contracts

**Milestone:** M1 — Honest orchestration  
**Priority:** P0  
**Implementation order:** 2  
**Depends on:** CC-001

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

Replace placeholder and inline agent behavior with versioned prompt assets and validated structured schemas for each major SDLC artifact.

## Verified current-state problem

- Agents currently generate generic Markdown from context.
- Prompt lifecycle components exist but are not the execution source of truth.
- Major artifacts lack enforceable machine-readable schemas.

## Primary scope and likely files

- prompts/lifecycle.py
- prompts/system/
- prompts/templates/
- agents/base.py
- models/artifact.py
- validators/prompt_evaluator.py
- validators/artifact_validator.py
- tests/test_prompt_lifecycle.py
- tests/test_prompt_regression.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define prompt metadata frontmatter: prompt ID, semantic version, owner, status, inputs, output schema, model/tool requirements, and changelog.
2. Create versioned prompts for product vision, requirements, user stories, architecture, ADR, project plan, code manifest, code review, QA remediation, security remediation, documentation, and release readiness.
3. Define typed schemas for those outputs; use stable IDs for requirements, stories, ADRs, tasks, findings, and files.
4. Add a prompt resolver to execution context and require production runs to use approved prompt versions.
5. Validate rendered variables before provider execution and validate structured results after.
6. Add deterministic regression fixtures and prompt quality checks to CI-ready commands.

## Prompt-engineering requirements

- Every prompt must define objective, inputs, constraints, required output, refusal/failure handling, and validation criteria.
- Structured output must include schema version.
- Prompt review may recommend changes but cannot auto-approve a system prompt.
- Record prompt ID, version, and content hash in execution metadata.

## Software-engineering requirements

- Retain backward compatibility for historical runs by pinning old prompt/version metadata.
- Malformed structured output is a failed attempt and must enter retry/escalation policy.
- No secret values may be stored in prompt fixtures.

## Acceptance criteria

- Every provider-backed agent references an approved prompt ID/version.
- Every major artifact validates against a typed schema.
- Unversioned changes to approved prompts fail validation.
- Prompt regression and artifact-schema tests pass.

## Required validation

- `python -m pytest tests/test_prompt_lifecycle.py tests/test_prompt_evaluation.py tests/test_prompt_regression.py tests/test_validators.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Prompt registry report
- Sample validated outputs for each artifact type
- Regression baseline diff

## Out of scope

- Live provider calls
- Automatic prompt rewriting
- Prompt authoring UI

## Rollback requirement

Revert prompt resolution while keeping the new schemas and validation fixtures available for the next iteration.

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

- Branch: `copilot/cc-002`
- Commit: `CC-002: Create managed prompts and structured artifact contracts`
- Draft PR: `CC-002 — Create managed prompts and structured artifact contracts`
