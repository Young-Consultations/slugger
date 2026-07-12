# GA-012: Connect one GitHub delivery path and complete CI/package distribution

**Priority:** P0  
**Implementation order:** 12  
**Depends on:** GA-011

## Objective

Use one GitHub path for issues, branch, draft PR, Actions, package evidence, and draft release candidate.

## Canonical implementation to keep

- One idempotent GitHub automation service.
- One CI workflow set.
- One package/release path.

## Code and behavior to remove

- Delete placeholder GitHub/CI/deployment/release agents.
- Delete duplicate GitHub wrappers.
- Delete obsolete release scripts/workflows.
- Delete incomplete package configuration.

## Primary scope

- services/github/
- agents/support/github_issues_agent.py
- agents/operations/
- .github/workflows/
- pyproject.toml
- scripts/release.py

## Ordered implementation steps

1. Create/update issues idempotently.
2. Publish files to a controlled branch.
3. Open draft PR and post evidence.
4. Dispatch/poll Actions.
5. Expand CI to lint, format, type, tests, coverage, security, dependency audit, package build, wheel install, acceptance, and YAML validation.
6. Fix pytest collection warnings.
7. Package all runtime modules and YAML/Markdown assets.
8. Generate packages, checksums, SBOM, provenance, and optional non-root container.
9. Create only a draft release candidate.
10. Delete duplicate delivery implementations.

## Definition of Done

- A clean wheel contains all runtime modules/assets.
- Installed wheel runs `slugger build`.
- GitHub resume creates no duplicates.
- CI enforces mandatory checks.
- Automation never approves, merges, or publishes.
- One delivery path remains.

## Required validation

- `python -m pytest tests/test_github_expanded.py tests/test_release_automation.py -q`
- `python -m pytest -q`
- Build and inspect wheel.
- Install wheel and run CLI.
- Validate workflow YAML.

## Rollback

Disable GitHub writes and leave all outputs draft.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-012`
- Commit: `GA-012: Connect one GitHub delivery path and complete CI/package distribution`
- Draft PR: `GA-012 — Connect one GitHub delivery path and complete CI/package distribution`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
