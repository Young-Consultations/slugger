# Slugger Remaining-Work Packets

Copy this directory into the repository at `prompts/tasks/remaining_work/`.

## Purpose

These 60 work packets convert the remaining AI Software Factory gaps into implementation-ready GitHub Copilot Agent assignments based on the current repository rather than the earlier high-level backlog.

## Execution Order

1. AI Provider Completion
2. Autonomous Agent Collaboration
3. Artifact Traceability
4. Human Approval System
5. Production Readiness and Generated-App Delivery
6. Prompt Lifecycle
7. Knowledge Base
8. Observability
9. Enterprise Hardening and Certification

The dependency line in each packet is authoritative when cross-epic dependencies exist.

## Copilot Agent Operating Rules

1. Assign exactly one packet per Copilot Agent session.
2. Require the agent to inspect current code and tests before editing.
3. Require a plan, focused branch, draft PR, tests, documentation, and Definition of Done evidence.
4. Do not accept invented external API endpoints; verify current official OpenAI, GitHub, and Canva documentation.
5. Keep live-provider tests opt-in and never expose credentials to pull-request jobs.
6. Update the completion matrix after every merged packet.

## Completion Rule

The project may claim at least 95% completion only after WP-060 proves at least 95% of committed in-scope requirements and 100% of P0 requirements with automated or approved manual evidence.

## Packet Index

| Packet | Epic | Title | Priority | Depends on |
|---|---:|---|---|---|
| WP-001 | 1 | Define task-oriented provider contracts | P0 | — |
| WP-002 | 1 | Wire Codex into bootstrap and provider selection | P0 | WP-001 |
| WP-003 | 1 | Implement production code-generation artifact pipeline | P0 | WP-001, WP-002 |
| WP-004 | 1 | Integrate Codex review and bounded refactor loop | P0 | WP-003, WP-012 |
| WP-005 | 1 | Connect ChatGPT prompt execution and review | P0 | WP-001, WP-035 |
| WP-006 | 1 | Complete Canva design-agent workflow | P0 | WP-001, WP-017 |
| WP-007 | 1 | Integrate GitHub repository and workflow automation | P0 | WP-003, WP-034 |
| WP-008 | 1 | Add provider health, fallback, and contract suite | P0 | WP-002, WP-005, WP-006, WP-007 |
| WP-009 | 2 | Inject message bus into runtime execution | P0 | WP-001 |
| WP-010 | 2 | Implement shared project context and memory handoff | P0 | WP-009 |
| WP-011 | 2 | Route typed artifacts between agents | P0 | WP-003, WP-010, WP-016 |
| WP-012 | 2 | Implement architect–developer–reviewer loop | P0 | WP-004, WP-011 |
| WP-013 | 2 | Implement QA remediation loop | P0 | WP-012, WP-029 |
| WP-014 | 2 | Implement security remediation loop | P0 | WP-013, WP-032 |
| WP-015 | 2 | Integrate retry, escalation, and terminal failure handling | P0 | WP-009, WP-012, WP-013, WP-014 |
| WP-016 | 3 | Replace in-memory artifact store with durable repository | P0 | WP-011 |
| WP-017 | 3 | Automatically capture and persist artifact lineage | P0 | WP-016 |
| WP-018 | 3 | Integrate artifact versioning and dependency invalidation | P0 | WP-017 |
| WP-019 | 3 | Generate project manifest and traceability matrix | P0 | WP-017, WP-018 |
| WP-020 | 3 | Expose traceability through CLI | P1 | WP-019 |
| WP-021 | 3 | Add traceability migration and consistency validation | P1 | WP-016, WP-017, WP-018, WP-019 |
| WP-022 | 4 | Extend workflow DSL with approval policies | P0 | WP-011 |
| WP-023 | 4 | Pause and resume workflows at approval gates | P0 | WP-022, WP-015 |
| WP-024 | 4 | Add approval management CLI | P0 | WP-023 |
| WP-025 | 4 | Persist immutable approval audit evidence | P0 | WP-023, WP-024 |
| WP-026 | 4 | Complete approval acceptance suite and runbook | P1 | WP-022, WP-023, WP-024, WP-025 |
| WP-027 | 5 | Materialize generated artifacts into safe workspace | P0 | WP-003, WP-016 |
| WP-028 | 5 | Implement application template contracts and selection | P0 | WP-027, WP-041 |
| WP-029 | 5 | Add isolated build and smoke-test runner | P0 | WP-027, WP-028 |
| WP-030 | 5 | Integrate coverage measurement and thresholds | P0 | WP-029 |
| WP-031 | 5 | Add lint, format, typing, coverage, and CI gates | P0 | WP-029 |
| WP-032 | 5 | Integrate source, dependency, and secret scanning | P0 | WP-029, WP-031 |
| WP-033 | 5 | Enforce documentation and deployment completeness | P0 | WP-028, WP-029 |
| WP-034 | 5 | Wire readiness evidence to release enforcement | P0 | WP-019, WP-025, WP-030, WP-031, WP-032, WP-033 |
| WP-035 | 6 | Register repository prompt files as versioned assets | P0 | WP-016 |
| WP-036 | 6 | Resolve and pin prompts during agent execution | P0 | WP-035, WP-010 |
| WP-037 | 6 | Enforce prompt evaluation and regression in CI | P0 | WP-035, WP-036 |
| WP-038 | 6 | Add structured ChatGPT prompt review policy | P1 | WP-005, WP-037 |
| WP-039 | 6 | Complete prompt approval, deprecation, and changelog | P1 | WP-035, WP-038 |
| WP-040 | 6 | Capture prompt execution provenance and effectiveness | P1 | WP-036, WP-047, WP-048 |
| WP-041 | 7 | Bootstrap and persist engineering knowledge index | P1 | WP-016 |
| WP-042 | 7 | Implement policy-aware knowledge retrieval | P1 | WP-041, WP-010 |
| WP-043 | 7 | Enforce standards across SDLC artifacts | P1 | WP-042, WP-012 |
| WP-044 | 7 | Capture approved lessons from reflection | P2 | WP-041, WP-025 |
| WP-045 | 7 | Add optional semantic retrieval with fallback | P2 | WP-041, WP-042, WP-008 |
| WP-046 | 7 | Complete knowledge quality gates and contributor guide | P2 | WP-041, WP-042, WP-043, WP-044 |
| WP-047 | 8 | Create unified execution event schema | P1 | WP-009 |
| WP-048 | 8 | Capture provider usage, cost, latency, and budgets | P1 | WP-001, WP-047 |
| WP-049 | 8 | Collect workflow performance and completion metrics | P1 | WP-047 |
| WP-050 | 8 | Correlate failure analytics and remediation outcomes | P1 | WP-015, WP-047, WP-049 |
| WP-051 | 8 | Expose operational dashboard and reports through CLI | P1 | WP-048, WP-049, WP-050 |
| WP-052 | 8 | Implement observability redaction, retention, and reliability | P1 | WP-047, WP-048, WP-051 |
| WP-053 | 9 | Enforce configuration validation and startup diagnostics | P0 | WP-008, WP-041 |
| WP-054 | 9 | Harden secrets and OAuth token lifecycle | P0 | WP-006, WP-007, WP-053 |
| WP-055 | 9 | Harden transactions and concurrent workflow execution | P0 | WP-016, WP-021, WP-023 |
| WP-056 | 9 | Harden plugin permissions, validation, and isolation | P1 | WP-053, WP-055 |
| WP-057 | 9 | Complete GitHub CI/CD and release governance | P0 | WP-007, WP-031, WP-032, WP-034 |
| WP-058 | 9 | Produce reproducible packages, container, and SBOM | P0 | WP-029, WP-031, WP-032, WP-057 |
| WP-059 | 9 | Create full idea-to-production acceptance suite | P0 | WP-006, WP-007, WP-013, WP-014, WP-019, WP-023, WP-034, WP-058 |
| WP-060 | 9 | Publish certification and 95% completion evidence | P0 | WP-026, WP-034, WP-051, WP-053, WP-057, WP-058, WP-059 |
