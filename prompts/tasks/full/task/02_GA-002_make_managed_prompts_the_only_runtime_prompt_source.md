# GA-002: Make managed prompts the only runtime prompt source

**Priority:** P0  
**Implementation order:** 2  
**Depends on:** GA-001

## Objective

Replace all inline production prompts with approved, versioned catalog prompts.

## Canonical implementation to keep

- `SdlcPromptCatalog` and the prompt lifecycle registry are the only runtime prompt sources.
- Prompt ID, version, hash, schema, and approval state are recorded for every provider execution.

## Code and behavior to remove

- Delete inline production prompt constants.
- Delete duplicate unregistered prompt templates.
- Delete tests validating obsolete inline-prompt behavior.

## Primary scope

- prompts/catalog.py
- prompts/lifecycle.py
- prompts/system/
- prompts/templates/
- agents/planning/
- agents/architecture/
- agents/development/
- models/execution.py

## Ordered implementation steps

1. Assign a managed prompt and output schema to every provider-backed agent.
2. Inject the prompt resolver into execution context.
3. Reject unapproved prompts in production.
4. Pin prompt versions for resume.
5. Add prompt regression checks.
6. Delete unused and duplicate prompt assets.

## Definition of Done

- No production agent contains a standalone prompt body.
- Every provider execution records prompt provenance.
- Unversioned approved-prompt changes fail validation.
- Resume uses the pinned prompt.
- Unused prompt files are removed.

## Required validation

- `python -m pytest tests/test_prompt_lifecycle.py tests/test_prompt_evaluation.py tests/test_prompt_regression.py -q`
- `python -m pytest -q`

## Rollback

Revert resolver and catalog migration together; never reintroduce unversioned prompts.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-002`
- Commit: `GA-002: Make managed prompts the only runtime prompt source`
- Draft PR: `GA-002 — Make managed prompts the only runtime prompt source`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
