# GA-003: Create one provider and service resolution path

**Priority:** P0  
**Implementation order:** 3  
**Depends on:** GA-001, GA-002

## Objective

Use one capability resolver for ChatGPT, Codex, Canva, GitHub, and embeddings.

## Canonical implementation to keep

- One resolver selects by capability, preference, profile, health, and explicit fallback policy.
- Mocks are development/test adapters only.

## Code and behavior to remove

- Delete hard-coded `provider='mock'` metadata.
- Delete duplicate provider selection logic.
- Rename or remove any generic completion wrapper labeled as a full Codex agent.

## Primary scope

- providers/
- services/
- orchestrator/bootstrap.py
- orchestrator/context.py
- agents/base.py
- models/provider.py
- config/settings.py

## Ordered implementation steps

1. Define the canonical capability list.
2. Implement one resolver and one health-diagnostic path.
3. Inject handles into execution context.
4. Add strict production mode without mock fallback.
5. Record selected implementation and fallback reason.
6. Delete duplicate registries/helpers.

## Definition of Done

- Every external capability uses the same resolver.
- Production fails before execution when a mandatory capability is unavailable.
- Mocks require explicit profile permission.
- No agent instantiates concrete providers directly.
- Selection tests cover every capability.

## Required validation

- `python -m pytest tests/test_provider_contracts.py tests/test_configuration_profiles.py tests/test_codex_provider.py tests/test_chatgpt_service.py tests/test_canva_service.py tests/test_github_expanded.py -q`
- `python -m pytest -q`

## Rollback

Switch to explicit mock profile; do not restore hard-coded providers.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-003`
- Commit: `GA-003: Create one provider and service resolution path`
- Draft PR: `GA-003 — Create one provider and service resolution path`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
