# Use Cases

## Actors

**Portfolio approver**, **organization router**, **requesting professional**, **Slugger operator**, **AI provider**, **dependency source**, **GitHub/target repository**, **reviewer**, **security/release authority**, and **capability owner**. External systems are actors only for contract interaction; their implementation is unknown.

## UC-01 — Produce a verified Python CLI draft

**Actors:** requesting professional (beneficiary), portfolio approver/router (initiators), provider, target, reviewer.  
**Preconditions:** approved complete intent; supported CLI class; registered target; provider and controlled environment available.  
**Primary flow:** (1) router delivers canonical request; (2) Slugger validates contract, authority, scope, target, identity and idempotency state; (3) user-visible scope/limits are recorded; (4) run/workspace and constrained provider request are established; (5) provider creates candidate; (6) Slugger inventories and validates it; (7) dependencies/install/tests/smoke run in isolation; (8) evidence is assembled; (9) current authority/target/evidence are rechecked; (10) one managed draft is published; (11) reviewer receives evidence and next action.  
**Alternatives:** an already complete matching draft is returned without provider invocation; an allowed transient phase is retried; publication is intentionally skipped for an approved local diagnostic profile, which cannot be labeled as published success.  
**Failures:** invalid/withdrawn authority, unsupported scope, provider failure, unsafe output, dependency/install/test/smoke failure, tampering, source mutation, target ambiguity, permission failure, or timeout blocks dependent actions and returns safe evidence.  
**Outcome/value:** a faster runnable draft with observed evidence and preserved human review authority.  
**Trace:** FR-INT-*, FR-SCP-01, FR-PRV-01, FR-VAL-01, FR-EXE-01, FR-TST-01, FR-SMK-01, FR-EVD-01, FR-PUB-*.

## UC-02 — Verify target integration without mutation

**Actors:** organization router, operator.  
**Primary flow:** route canonical verification request; validate contract/registration/policy and safe product readiness; emit validated canonical evidence/result.  
**Alternatives:** contract or target mismatch returns a rejection useful for registration correction.  
**Failures:** unavailable validator, unsupported version, missing registration/context, or failed safe check yields non-passing result.  
**Expected outcome/value:** integration wiring is proven without provider cost or repository mutation.  
**Trace:** FR-INT-01/02; AC-INT-02c; NFR-AUT-01.

## UC-03 — Redeliver the same logical request

**Actors:** router, operator, target.  
**Primary flow:** Slugger validates stable identity/digest; classifies durable target state; recognizes one complete owned draft; confirms evidence; returns reuse result without regenerating.  
**Alternatives:** no target state exists, so normal processing proceeds; safe incomplete matching state resumes after revalidation.  
**Failures:** changed immutable input, multiple matches, unowned branch, marker mismatch, wrong base, non-draft, closed/merged state, or indeterminate service result is preserved and blocked.  
**Expected outcome/value:** at-least-once delivery does not duplicate cost or overwrite work.  
**Trace:** FR-RUN-01, FR-IDM-01, NFR-REL-02.

## UC-04 — Recover an interrupted run

**Actors:** operator, requesting professional.  
**Primary flow:** inspect correlated status/evidence; request resume; Slugger locates last trustworthy boundary; revalidates authority, configuration, artifact integrity and target; reruns stale dependent gates; records lineage; completes or returns a new actionable failure.  
**Alternatives:** operator starts a separately identified run when policy forbids resume.  
**Failures:** corrupt/missing state, ambiguous ownership, changed inputs, expired authority, or unsafe workspace causes non-destructive refusal.  
**Expected outcome/value:** recovery avoids both full repetition where safe and gate bypass.  
**Trace:** FR-RUN-02, FR-REC-01, FR-ERR-01, NFR-REC-*.

## UC-05 — Review and decide on a generated draft

**Actors:** reviewer, architect, security/release authority.  
**Primary flow:** open draft; understand source/scope; inspect candidate, inventory, verified checks, exclusions, and residual decisions; request change or independently mark ready/merge under target governance.  
**Alternatives:** reject/close externally; request a newly approved delivery after material scope change.  
**Failures:** evidence missing/integrity-invalid/incomprehensible causes no advancement and is escalated. Slugger does not decide for reviewer.  
**Expected outcome/value:** informed accountable review rather than blind trust in AI output.  
**Trace:** FR-EVD-01, FR-PUB-02, FR-GOV-01, NFR-USA-01.

## UC-06 — Diagnose a blocked or failed run

**Actors:** operator, requesting professional, provider/platform owner when external.  
**Primary flow:** query status; identify phase/category/impact/retryability; inspect redacted bounded evidence; follow authorized remediation; retry if permitted.  
**Alternatives:** escalate contract, provider, security, or target issue to its owner.  
**Failures:** sensitive raw output is quarantined rather than shown; missing correlation becomes an internal defect and publication remains blocked.  
**Expected outcome/value:** lower recovery effort without disclosure or unsafe workarounds.  
**Trace:** FR-ERR-01, NFR-OBS-*, NFR-ACC-02.

## UC-07 — Propose and promote a new capability (post-MVP)

**Actors:** capability owner, architect, security authority, product owner, representative users.  
**Primary flow:** document user value/boundary/contracts; define measurable requirements and human gate; threat-model; implement independently; pass contract/security/reliability/UX evidence; approve status/catalog change; monitor after release.  
**Alternatives:** retain as experimental or reject.  
**Failures:** missing owner, ambiguous authority, insufficient isolation/evidence, regressions, or unsupported dependency prevents promotion.  
**Expected outcome/value:** deliberate expansion without converting research code into an implied supported product.  
**Trace:** FR-CAT-01, FR-LCM-02, FR-EXT-01, BR-20.

## UC-08 — Compose future lifecycle phases (post-MVP)

**Actors:** requesting professional, phase owners, human reviewers, automation consumer.  
**Primary flow:** select approved capabilities; validate reviewed upstream artifacts and compatibility; execute one bounded phase; validate/evidence its output; pause for named human decision; pass approved artifact to the next phase.  
**Alternatives:** replace a phase/provider, return upstream for revision, pause/resume, or stop after a useful artifact.  
**Failures:** incompatible/unapproved/missing artifact, invalid evidence, or rejected human gate blocks only dependent phases and marks impact.  
**Expected outcome/value:** end-to-end leverage with traceability and independent decision points.  
**Trace:** FR-LCM-01/02, VG-06.
