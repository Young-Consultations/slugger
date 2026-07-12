# GA-001: Freeze the canonical architecture and delete alternate runtime paths

**Priority:** P0  
**Implementation order:** 1  
**Depends on:** None

## Objective

Define and enforce the single supported execution path before further integration work.

## Canonical implementation to keep

- `full-sdlc-v2.yaml` is the only default production workflow.
- `AppManifest` is the only generated-application representation.
- `SQLiteArtifactStore` and the selected durable workflow database are the production persistence path.
- `DurableApprovalStore` is the only approval persistence path.
- `IsolatedBuildRunner` is the only generated-code execution path after hardening.

## Code and behavior to remove

- Remove or archive the old eight-step `full-sdlc.yaml` as an executable default.
- Remove runtime logic that silently falls back to obsolete workflows.
- Remove duplicate placeholder recipes that overlap the canonical path.
- Remove undocumented compatibility flags that reactivate old behavior.

## Primary scope

- orchestrator/orchestrator.py
- orchestrator/bootstrap.py
- workflow/recipes/
- config/defaults.yaml
- config/schema.yaml
- README.md
- docs/architecture.md
- docs/adr/

## Ordered implementation steps

1. Write an ADR naming the canonical workflow, artifact model, persistence adapters, approval store, and build runner.
2. Add architecture invariant tests for canonical defaults.
3. Change `slugger build` to invoke only the canonical workflow.
4. Provide a migration error for historical workflows that cannot resume safely.
5. Delete obsolete recipes and update tests.

## Definition of Done

- `slugger build` selects one workflow with no silent fallback.
- Only one production recipe remains active.
- Architecture docs match runtime defaults.
- Obsolete workflow tests/configuration are deleted.
- All workflow tests pass.

## Required validation

- `python -m pytest tests/test_orchestration_pipeline.py tests/test_configuration_profiles.py -q`
- `python -m pytest -q`
- Run `slugger build` and show the selected workflow.

## Rollback

Restore a previous recipe only for historical migration, never as the default.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-001`
- Commit: `GA-001: Freeze the canonical architecture and delete alternate runtime paths`
- Draft PR: `GA-001 — Freeze the canonical architecture and delete alternate runtime paths`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
