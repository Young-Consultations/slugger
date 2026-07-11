# CC-017: Complete GitHub automation, CI quality gates, packaging, and release candidate creation

**Milestone:** M8 — Repository delivery  
**Priority:** P0  
**Implementation order:** 17  
**Depends on:** CC-012, CC-016

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

Use GitHub as the repository/workflow agent: create/update issues, publish a branch, open a draft PR, dispatch/poll Actions, post evidence, and create an approved draft release candidate with package artifacts.

## Verified current-state problem

- GitHub REST clients exist but the main workflow does not execute repository lifecycle automation.
- CI currently runs pytest only.
- No generated application package/SBOM/release evidence is produced.

## Primary scope and likely files

- services/github/
- agents/support/github_issues_agent.py
- agents/operations/ci_cd_agent.py
- agents/operations/release_agent.py
- .github/workflows/
- .github/PULL_REQUEST_TEMPLATE.md
- scripts/release.py
- pyproject.toml
- tests/test_github_expanded.py
- tests/test_release_automation.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Create an idempotent repository automation service using persisted external IDs.
2. Map project tasks/findings to GitHub issues and update rather than duplicate them.
3. Publish generated files to a controlled branch and open a draft PR.
4. Post traceability, test, security, readiness, and approval summaries to the PR.
5. Dispatch/poll Actions and treat failed checks as release-blocking evidence.
6. Expand Slugger CI to format/lint, type check, tests, coverage, security, dependency audit, package build, and acceptance tests.
7. Resolve the seven pytest collection warnings.
8. Build wheel/source artifacts and optional non-root container; generate checksums, SBOM, and provenance.
9. Create only a draft release candidate after all gates and final approval; never merge or publish automatically.
10. Add Copilot Agent repository instructions and issue/PR templates referencing task IDs and DoD evidence.

## Prompt-engineering requirements

- Copilot tasks must reference the exact managed task prompt/version.
- PR summaries must be generated from persisted evidence, not free-form claims.

## Software-engineering requirements

- Use least-privilege tokens and versioned REST API requests.
- Fork/untrusted PR workflows receive no write secrets.
- All write operations support dry-run and idempotency.

## Acceptance criteria

- A mock GitHub integration produces one issue set, one branch, one draft PR, one Actions run, and one draft release candidate without duplicates after resume.
- CI enforces all mandatory checks.
- Packages include checksums, SBOM, provenance, and smoke-test evidence.
- Automation cannot approve/merge/publish its own change.

## Required validation

- `python -m pytest tests/test_github_expanded.py tests/test_release_automation.py -q`
- `python -m pytest -q`
- Validate GitHub workflow YAML
- Build/install package in a clean environment

## Pull-request evidence

- Repository automation
- Expanded CI
- Templates/instructions
- Packages/SBOM/provenance
- Mock lifecycle tests

## Out of scope

- Organization settings changes
- Automatic merge
- Published production release

## Rollback requirement

Leave the PR and release as draft, disable writes through configuration, and retain local packages/evidence.

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

- Branch: `copilot/cc-017`
- Commit: `CC-017: Complete GitHub automation, CI quality gates, packaging, and release candidate creation`
- Draft PR: `CC-017 — Complete GitHub automation, CI quality gates, packaging, and release candidate creation`
