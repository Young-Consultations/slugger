# GA-004: Complete planning, architecture, ADR, and design stages

**Priority:** P0  
**Implementation order:** 4  
**Depends on:** GA-002, GA-003

## Objective

Produce validated planning, architecture, ADR, and design artifacts from the user's idea.

## Canonical implementation to keep

- ChatGPT service for planning and prompt review.
- Canva service or durable manual design handoff.
- Typed artifacts with stable requirement and decision IDs.

## Code and behavior to remove

- Delete placeholder agents that only echo context.
- Delete duplicate architecture/design artifact classes.
- Delete manual handoff behavior that reports completion without a pending state.

## Primary scope

- agents/planning/
- agents/architecture/
- services/chatgpt/
- services/canva/
- models/artifact.py
- workflow/recipes/full-sdlc-v2.yaml

## Ordered implementation steps

1. Generate product vision, requirements, stories, acceptance criteria, architecture, ADRs, API design, and plan.
2. Generate a Canva brief and either export a design or enter durable `awaiting_design`.
3. Ensure manual handoff emits required pending artifacts.
4. Require design approval bound to exact versions.
5. Map all outputs to requirement IDs.
6. Delete placeholder Markdown-only implementations.

## Definition of Done

- The canonical workflow reaches implementation in deterministic offline mode.
- Canva manual handoff pauses cleanly.
- All planning/design artifacts validate.
- The idea is traceable through requirements, architecture, ADRs, and design.
- No placeholder echo agents remain active.

## Required validation

- `python -m pytest tests/test_chatgpt_service.py tests/test_canva_design_agent.py tests/test_orchestration_pipeline.py tests/test_artifact_lineage.py -q`
- `python -m pytest -q`

## Rollback

Disable live Canva and use durable manual handoff.

## GitHub Agent instructions

- Read `MASTER_GITHUB_AGENT_PROMPT.md`.
- Branch: `github-agent/ga-004`
- Commit: `GA-004: Complete planning, architecture, ADR, and design stages`
- Draft PR: `GA-004 — Complete planning, architecture, ADR, and design stages`
- Include a removal summary listing deleted files and obsolete symbols.
- Do not merge until every Definition of Done item has objective evidence.
