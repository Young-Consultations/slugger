# GA-006: Make AppManifest the only generated application output

**Priority:** P0  
**Implementation order:** 6  
**Depends on:** GA-004, GA-005

## Objective

Replace Markdown code artifacts with one validated multi-file application manifest.

## Canonical implementation to keep

- `AppManifest` is the sole source of generated files.
- Trusted template manifests define required files and commands.

## Code and behavior to remove

- Delete Markdown code-scaffold generation.
- Delete alternate manifest classes/parsers.
- Delete tests accepting code fences as successful generation.

## Primary scope

- models/app_manifest.py
- agents/development/code_generator_agent.py
- templates/
- validators/artifact_validator.py
- tests/test_sample_projects.py

## Ordered implementation steps

1. Generate AppManifest through Codex from approved artifacts.
2. Validate paths, syntax, dependencies, required files, sizes, checksums, and mappings.
3. Move executable commands into trusted templates.
4. Reject model-provided commands.
5. Remove incomplete templates.
6. Delete code-fence parsing.

## Definition of Done

- `slugger build` produces a valid AppManifest.
- Every file maps to immutable IDs.
- No generated command is executable.
- Unsafe/incomplete manifests fail before materialization.
- Only complete supported templates remain.

## Required validation

- `python -m pytest tests/test_sample_projects.py tests/test_validators.py tests/test_orchestration_pipeline.py -q`
- `python -m pytest -q`

## Rollback

Restore the last validated manifest; never fall back to Markdown.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-006`
- Commit: `GA-006: Make AppManifest the only generated application output`
- Draft PR: `GA-006 — Make AppManifest the only generated application output`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
