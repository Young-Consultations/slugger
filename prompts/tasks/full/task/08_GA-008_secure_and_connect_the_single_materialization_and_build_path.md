# GA-008: Secure and connect the single materialization and build path

**Priority:** P0  
**Implementation order:** 8  
**Depends on:** GA-006, GA-007

## Objective

Use one safe materializer and one truly isolated runner for all generated applications.

## Canonical implementation to keep

- `ProjectMaterializer` is the only file writer.
- `IsolatedBuildRunner` is the only executor.
- Template-owned command plans are the only command source.

## Code and behavior to remove

- Delete placeholder TestRunner behavior.
- Delete direct host subprocess bypasses.
- Delete unrestricted-command options.
- Delete duplicate materializers/runners.

## Primary scope

- materializer/workspace.py
- materializer/build_runner.py
- agents/qa/test_runner_agent.py
- templates/
- config/settings.py

## Ordered implementation steps

1. Make allowlists mandatory and template-owned.
2. Run in a dedicated venv or container.
3. Disable network by default.
4. Set resource/time/output/process limits.
5. Use explicit argv arrays.
6. Connect materialization and execution to the workflow.
7. Run install, compile, lint, type, tests, coverage, security, dependency audit, and smoke test.
8. Delete all bypasses.

## Definition of Done

- A generated CLI app installs and smoke-runs.
- A malicious manifest cannot execute host commands.
- Host secrets/home files are unavailable.
- Placeholder reports are removed.
- One materializer and runner remain.

## Required validation

- `python -m pytest tests/test_project_materializer.py tests/test_build_runner.py tests/test_mandatory_tests.py tests/test_security_scanning.py -q`
- `python -m pytest -q`
- Run a real generated CLI fixture.

## Rollback

Disable execution and retain generated-not-validated state.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-008`
- Commit: `GA-008: Secure and connect the single materialization and build path`
- Draft PR: `GA-008 — Secure and connect the single materialization and build path`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
