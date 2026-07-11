# Implementation Order

Execute tasks in numeric order unless every listed dependency is already merged. Do not run more than one task against the same high-conflict subsystem simultaneously.

## Milestones

### M1 — Honest orchestration

- **CC-001 — Correct workflow truthfulness and propagate the user idea** — P0; depends on none.
- **CC-002 — Create managed prompts and structured artifact contracts** — P0; depends on CC-001.

### M2 — Real AI agents

- **CC-003 — Implement capability-based runtime provider and service resolution** — P0; depends on CC-001, CC-002.
- **CC-004 — Connect ChatGPT to planning and prompt review** — P0; depends on CC-002, CC-003.
- **CC-005 — Replace the fake Codex wrapper with a true Codex coding-agent adapter** — P0; depends on CC-002, CC-003.
- **CC-006 — Complete Canva design generation, export, and approval handoff** — P0; depends on CC-003, CC-004.

### M3 — Runnable output

- **CC-007 — Generate a validated multi-file Python application manifest** — P0; depends on CC-002, CC-004, CC-005, CC-006.
- **CC-008 — Materialize application files into a safe, reproducible workspace** — P0; depends on CC-007.
- **CC-009 — Build, test, analyze, and smoke-run generated applications in isolation** — P0; depends on CC-008.

### M4 — Autonomous quality

- **CC-010 — Implement bounded code-review, QA, and security remediation loops** — P0; depends on CC-005, CC-009.

### M5 — Auditability

- **CC-011 — Persist artifacts, versions, lineage, and workflow state durably** — P0; depends on CC-001, CC-007, CC-008.
- **CC-012 — Fix human approval persistence, quorum, CLI decisions, and resume security** — P0; depends on CC-011.

### M6 — Governed intelligence

- **CC-013 — Inject knowledge, standards, and project memory into agent context** — P1; depends on CC-002, CC-011.
- **CC-014 — Instrument executions, token budgets, cost, failures, and completion evidence** — P1; depends on CC-003, CC-011.

### M7 — Product workflow

- **CC-015 — Replace the eight-step placeholder recipe with the real full AI-SDLC** — P0; depends on CC-004, CC-005, CC-006, CC-010, CC-012, CC-013, CC-014.
- **CC-016 — Collect authoritative readiness evidence and enforce release gates** — P0; depends on CC-009, CC-010, CC-011, CC-012, CC-015.

### M8 — Repository delivery

- **CC-017 — Complete GitHub automation, CI quality gates, packaging, and release candidate creation** — P0; depends on CC-012, CC-016.

### M9 — Acceptance

- **CC-018 — Prove idea-to-production behavior and generate the 95% completion certification** — P0; depends on CC-015, CC-016, CC-017.

## Parallel work guidance

- CC-004 and CC-005 may proceed in parallel after CC-003.
- CC-006 may proceed after CC-004 while CC-005 is underway, but CC-007 waits for both.
- CC-013 and CC-014 may proceed in parallel after durable storage is merged.
- CC-017 must not start release writes until CC-016 is merged.
- CC-018 is the final acceptance and certification gate.
