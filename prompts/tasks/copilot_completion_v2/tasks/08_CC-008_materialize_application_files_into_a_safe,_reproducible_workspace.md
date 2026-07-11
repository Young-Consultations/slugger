# CC-008: Materialize application files into a safe, reproducible workspace

**Milestone:** M3 — Runnable output  
**Priority:** P0  
**Implementation order:** 8  
**Depends on:** CC-007

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

Write a validated application manifest to an isolated workspace atomically and create a file inventory suitable for build, review, and release evidence.

## Verified current-state problem

- Generated code is not written as an application.
- No workspace lifecycle, atomic publication, or file checksum inventory exists.

## Primary scope and likely files

- services/project_materializer.py
- models/project.py
- models/artifact_store.py
- config/settings.py
- orchestrator/orchestrator.py
- tests/test_project_materializer.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define staging, active, failed, and released workspace states.
2. Create workspace roots under configured allowed directories.
3. Revalidate paths, file types, file sizes, duplicates, encodings, and symlink behavior at write time.
4. Write all files into staging, verify checksums, then atomically publish.
5. Create a deterministic file inventory mapping each file to source artifact/version and checksum.
6. Support idempotent resume and preserve failed-workspace evidence without overwriting users' files.
7. Add clean-up and retention behavior for temporary workspaces.

## Prompt-engineering requirements

- No new model prompt is needed; consume only the validated manifest.
- Do not allow model output to choose the workspace root.

## Software-engineering requirements

- Never execute code during materialization.
- Never overwrite an existing non-Slugger directory.
- Restrictive permissions and atomic writes are required.

## Acceptance criteria

- A validated manifest becomes a real installable project directory.
- Unsafe paths cannot escape the workspace.
- Partial failures do not publish an active workspace.
- Repeated resume does not duplicate or corrupt files.

## Required validation

- `python -m pytest tests/test_project_materializer.py tests/test_workflow_persistence.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Materializer
- File inventory
- Recovery tests
- Workspace configuration documentation

## Out of scope

- Installing dependencies
- Running generated code
- Git initialization

## Rollback requirement

Leave the prior active workspace untouched and restore from its file inventory.

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

- Branch: `copilot/cc-008`
- Commit: `CC-008: Materialize application files into a safe, reproducible workspace`
- Draft PR: `CC-008 — Materialize application files into a safe, reproducible workspace`
