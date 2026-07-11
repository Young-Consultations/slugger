# CC-007: Generate a validated multi-file Python application manifest

**Milestone:** M3 — Runnable output  
**Priority:** P0  
**Implementation order:** 7  
**Depends on:** CC-002, CC-004, CC-005, CC-006

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

Convert approved requirements, architecture, design, and implementation decisions into a validated, multi-file Python application manifest rather than a Markdown scaffold.

## Verified current-state problem

- `CodeGeneratorAgent` returns one Markdown artifact with embedded example files.
- There is no safe file manifest, template contract, or required-file validation.

## Primary scope and likely files

- agents/development/code_generator_agent.py
- models/artifact.py
- models/project.py
- templates/
- prompts/templates/
- validators/artifact_validator.py
- tests/test_sample_projects.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define a schema-versioned application manifest containing app metadata, template ID/version, files, path, content/checksum, ownership, mode, artifact parents, and generated commands.
2. Define initial supported templates: CLI application and FastAPI service; add Streamlit only if it can meet the same acceptance criteria.
3. Require code generation to produce/modify the manifest through the Codex agent.
4. Validate required files, package layout, Python syntax, dependency policy, path safety, duplicate paths, and maximum sizes.
5. Reject absolute paths, traversal, symlink instructions, device paths, credential files, and unapproved binaries.
6. Add golden fixture manifests and malformed-output tests.

## Prompt-engineering requirements

- The code-generation prompt must require schema-valid JSON or equivalent typed output.
- Each file must map to requirement/story/task IDs.
- The final summary must identify unresolved assumptions and generated test coverage intent.

## Software-engineering requirements

- Treat all model output as untrusted.
- Do not write files in this task; validation precedes materialization.
- Dependency versions must follow a documented policy.

## Acceptance criteria

- A task-tracker idea produces a validated CLI application manifest with source, tests, README, and `pyproject.toml`.
- A FastAPI fixture produces the required application and API test files.
- Unsafe or incomplete manifests are rejected.
- Markdown-only code scaffold output is removed from the primary path.

## Required validation

- `python -m pytest tests/test_sample_projects.py tests/test_orchestration_pipeline.py tests/test_validators.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Manifest schema
- Template contracts
- Golden valid/invalid fixtures
- Generation integration

## Out of scope

- Writing project files
- Executing generated code
- Publishing to GitHub

## Rollback requirement

Re-enable the last validated manifest version; do not return to unvalidated Markdown parsing.

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

- Branch: `copilot/cc-007`
- Commit: `CC-007: Generate a validated multi-file Python application manifest`
- Draft PR: `CC-007 — Generate a validated multi-file Python application manifest`
