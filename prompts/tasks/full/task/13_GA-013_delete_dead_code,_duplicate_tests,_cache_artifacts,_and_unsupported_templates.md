# GA-013: Delete dead code, duplicate tests, cache artifacts, and unsupported templates

**Priority:** P0  
**Implementation order:** 13  
**Depends on:** GA-001, GA-002, GA-003, GA-004, GA-005, GA-006, GA-007, GA-008, GA-009, GA-010, GA-011, GA-012

## Objective

Perform final repository consolidation after canonical integrations are complete.

## Canonical implementation to keep

- All canonical implementations selected in GA-001 through GA-012.

## Code and behavior to remove

- All unreferenced placeholder agents.
- Old recipes and persistence adapters.
- Duplicate provider/service wrappers.
- Inline prompts and Markdown scaffolds.
- Duplicate readiness/approval/finding models.
- Unsupported templates.
- Dead tests and fixtures.
- Committed `.pyc`, caches, runtime DBs, workspaces, and temporary files.

## Primary scope

- entire repository
- pyproject.toml
- .gitignore
- README.md
- docs/
- tests/
- scripts/

## Ordered implementation steps

1. Run static import/reference analysis.
2. Remove dead code and update imports.
3. Remove duplicate tests.
4. Mark historical ADRs superseded.
5. Update package discovery/data.
6. Strengthen `.gitignore`.
7. Run compile, test, package, install, and CLI checks.
8. Document final architecture and extension points.

## Definition of Done

- No obsolete production path is importable.
- No generated/cache/runtime artifacts are committed.
- Package contains all required assets.
- Docs describe only supported behavior.
- Tests pass after deletion.

## Required validation

- `python -m compileall agents core models orchestrator providers services workflow materializer prompts`
- `python -m pytest -q`
- Build/install wheel.
- Run dead-code/reference checks.

## Rollback

Restore only a deletion proven to break a supported path.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-013`
- Commit: `GA-013: Delete dead code, duplicate tests, cache artifacts, and unsupported templates`
- Draft PR: `GA-013 — Delete dead code, duplicate tests, cache artifacts, and unsupported templates`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
