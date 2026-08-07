# Architecture Traceability Matrix

## Organization next-MVP slice

| Included requirements | Design/interface realization | Required conformance evidence |
|---|---|---|
| FR-INT-01, FR-INT-02 | IF-01/IF-04; ADR-009/ADR-013; inbound and authority adapters | supported/malformed/version/target and valid/invalid/stale/withdrawn fixtures |
| FR-RUN-01, FR-IDM-01 | coordinator, IF-11/IF-12; ADR-003/ADR-007 | duplicate/reuse/conflict and interrupted-publication fixtures |
| FR-WS-01, FR-PRV-01 | workspace/Codex ports; ADR-004/ADR-008 | fake implement, verify-no-call, outside-scope denial and network trap |
| FR-VAL-01, FR-TST-01, FR-EVD-01 | validation/evidence adapters; ADR-004/ADR-006/ADR-011 | deterministic pass/fail evidence and safe-error fixtures |
| FR-PUB-01, FR-PUB-02 | GitHub publication adapter/IF-12; ADR-007/ADR-013 | simulated create/reuse, one visible effect, draft-only assertion |
| FR-ERR-01, FR-RES-01 | IF-02, result adapter/outbox; ADR-009/ADR-011/ADR-012 | official-validator coverage for every outcome and redelivery |
| FR-CNF-01 | conformance composition; ADR-014 | merge-blocking, no-secret/no-network/no-real-publication suite |

This slice is narrower than the architecture's long-term factory. Deferred requirements and external blockers are recorded in [`docs/next-mvp.md`](../next-mvp.md); rows elsewhere in this document are not implicitly selected for the organization release.

## Traceability method

The requirements matrix remains authoritative for Vision → business → requirement → acceptance/test. This matrix continues the chain through architecture. Future implementation records add `IMP-*` module/service, migration and test IDs in the final column; an architecture row is not evidence that code exists.

| Vision / business goal | Requirements and rules | Architecture decision / mechanism | Components | Interfaces | Future implementation and proof |
|---|---|---|---|---|---|
| VG-01 governed transformation / BO-01, BO-03 | FR-INT-01, FR-SCP-01, FR-PRM-01, FR-PRV-01, FR-VAL/DEP/EXE/TST/SMK/PUB-01; BR-06–12 | ADR-001, 004, 005, 011; single pipeline, capability profile, hostile-candidate gates | Contract Boundary, Scope, Prompt, Provider, Inventory, Verifier, Gates, Publication | IF-01, 03–09, 12 | IMP-TBD; FTC-E2E-01, FTC-GATE-01, golden profile fixture |
| VG-02 traceability / BO-02 | FR-RUN-01/02, FR-ART-01, FR-EVD-01, FR-ERR-01, FR-LCM-01; BR-12, 14, 28–29 | ADR-003, 006, 012; durable history and bound evidence | Identity, Coordinator, Inventory, Evidence/Audit, Diagnostics | IF-02, 10, 11, 14, 15 | IMP-TBD; FTC-TRC-01, FTC-EVD-01/02, FTC-LOG-01 |
| VG-03 human authority / BO-02, BO-05 | FR-INT-02, FR-PUB-01/02, FR-GOV-01, FR-LCM-02; BR-01–05, 19 | ADR-001, 008, 009; external authority recheck and draft-only limit | Authority/Scope, Gate Engine, Publication, Result | IF-01–05, 12, 13 | IMP-TBD; FTC-AUTH-01/02, FTC-PR-01/02 |
| VG-04 safe isolation / BO-03 | FR-PRV-01, FR-WS-01/02, FR-ART/VAL/DEP/EXE/PUB-01; BR-08–11, 22–24 | ADR-004, 008; phase trust zones and exact manifest | Provider, Workspace, Inventory, Dependency, Verifier, Secret Broker | IF-06–10, 12–14 | IMP-TBD; FTC-SEC-01–04, FTC-SRC-01 |
| VG-05 reliable recovery / BO-04 | FR-RUN-01/02, FR-SMK-01, FR-IDM-01, FR-REC-01, FR-ERR-01; BR-13, 15–17, 21, 27 | ADR-003, 007, 011; persisted state, stable ownership, reconcile-before-retry | Identity, Coordinator, Gate, Publication, Diagnostics | IF-06, 09–12, 14 | IMP-TBD; FTC-IDM-01/02, FTC-REC-01/02, FTC-TGT-01 |
| VG-06 composable evolution / BO-06 | FR-CAT-01, FR-PRV-01, FR-LCM-01/02, FR-EXT-01; BR-20, 25–26, 31–32 | ADR-002, 005, 009, 010; ports, promotion profiles, quarantine | Catalog, all port adapters, Extension Registry | IF-03, 05–17 | IMP-TBD; FTC-ARC-01, FTC-CON-01, FTC-EXT-01, FTC-PROM-01 |
| VG-07 organizational boundary / BO-05 | FR-INT-01/02, FR-PUB-02, FR-GOV-01; BR-03–04, 18–19, 31 | ADR-009; attributed facts and externally owned contracts | Contract Boundary, Authority, Result, Publication | IF-01, 02, 04, 12, 17 | IMP-TBD; FTC-CTR-01/02, FTC-BOUND-01/02 |

## Quality-attribute coverage

| NFR family | Architectural realization | Verification direction |
|---|---|---|
| Performance/scalability | Early preflight, completed-delivery reuse, independent pools, quotas/backpressure | Load/queue/cost baselines; keyed concurrency tests |
| Reliability/recovery | Atomic boundaries, leases/CAS, outbox, reconciliation, immutable evidence | Kill each phase; backup/restore; external ambiguity injection |
| Security/integrity | Trust zones, phase credentials, hostile candidate, exact manifest, deny defaults | Threat corpus, sandbox/egress/canary/tamper tests |
| Observability/audit | Structured safe signals plus distinct mandatory evidence/audit | Correlation/redaction/completeness and alert exercises |
| Maintainability/testability | Dependency rule, pure policies, typed ports, fixtures, modular monolith | Architecture tests, fake-adapter conformance, mutation/fault tests |
| Usability/accessibility | Equivalent machine/human result, limitations and next action | Representative-user comprehension/accessibility checks |
| Extensibility/interoperability | Capability profiles, port manifests, semver, external schema ownership | Substitute adapter and compatibility/rollback tests |
| Configuration/automation/AI | Typed effective config/digest, headless commands, bounded machine actors | Precedence/invalid config tests; same-policy entry-point tests |

## Requirement-to-design change control

Every architecture/implementation change record must include: vision/business/requirement/rule IDs; affected ADR/component/interface/state/data classifications; new/changed assumptions and external owner validation; security/quality impact; compatible and breaking versions; migration/in-flight/rollback plan; future test/evidence IDs; and documentation updates. Untraced supported behavior is a defect.

## AI-SDLC handoff template

```yaml
change_id: IMP-TBD
requirements: [FR-TBD, NFR-TBD, BR-TBD]
architecture: [ADR-TBD, component-name, IF-TBD]
preconditions: []
invariants: []
unknowns_blocking: []
files_or_units_allowed: []
contracts_and_fixtures: []
negative_and_failure_tests: []
security_and_data_classification: []
migration_and_rollback: []
evidence_expected: []
human_review_owner: TBD
```

AI agents must stop rather than manufacture missing authority, external schema, status, secret, target ownership or promotion evidence.
