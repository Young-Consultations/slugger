# CC-006: Complete Canva design generation, export, and approval handoff

**Milestone:** M2 — Real AI agents  
**Priority:** P0  
**Implementation order:** 6  
**Depends on:** CC-003, CC-004

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

Create a usable design stage that converts requirements into a Canva design brief, uses documented Canva capabilities, exports assets, and supplies approved design artifacts to code generation.

## Verified current-state problem

- The Canva agent selects the first existing design or emits a placeholder.
- The standard full-SDLC recipe does not invoke Canva.
- OAuth/export lifecycle and downstream design consumption are incomplete.

## Primary scope and likely files

- agents/architecture/canva_design_agent.py
- services/canva/
- workflow/recipes/full-sdlc.yaml
- config/settings.py
- workflow/approvals.py
- tests/test_canva_design_agent.py
- tests/test_canva_service.py

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Define a structured design brief from requirements, user stories, brand constraints, screen inventory, and accessibility requirements.
2. Implement supported paths for brand-template autofill or documented Canva MCP/Connect operations; feature-flag preview capabilities.
3. Implement OAuth token lifecycle and required scope diagnostics.
4. Poll export jobs with bounded retry/timeout and ingest export metadata/checksums.
5. Produce design manifest, screen/component inventory, design tokens, accessibility notes, and requirement mappings.
6. Add a manual-design handoff state when automatic design creation is unsupported.
7. Require design approval before code generation consumes design artifacts.
8. Add deterministic mock and HTTP-contract tests.

## Prompt-engineering requirements

- The design prompt/brief must be a versioned artifact.
- Design output must map every screen/component to requirement IDs.
- A placeholder design cannot count as approved design completion.

## Software-engineering requirements

- Use OAuth Authorization Code with PKCE where required.
- Never store Canva tokens in artifacts or logs.
- Downloaded assets require MIME type, size, checksum, and source metadata.

## Acceptance criteria

- The full workflow contains a Canva design stage.
- A mock run produces validated design artifacts consumed by code generation.
- Unsupported automation pauses for an explicit manual handoff rather than succeeding.
- Approval is tied to exact design artifact versions.

## Required validation

- `python -m pytest tests/test_canva_service.py tests/test_canva_design_agent.py tests/test_workflow_approval_integration.py -q`
- `python -m pytest -q`

## Pull-request evidence

- Design brief and manifest
- Export ingestion
- Approval handoff
- Mock/contract tests

## Out of scope

- Canva UI application
- Undocumented design endpoints
- Automatic publishing

## Rollback requirement

Disable automatic Canva operations and use the manual handoff path; preserve design schema and approval requirements.

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

- Branch: `copilot/cc-006`
- Commit: `CC-006: Complete Canva design generation, export, and approval handoff`
- Draft PR: `CC-006 — Complete Canva design generation, export, and approval handoff`
