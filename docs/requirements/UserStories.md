# User Stories

## Governed intake and scope

### US-01 — Faithful approved intake
**Role:** technically capable product owner. **Goal:** have approved intent enter generation with its constraints and source intact. **Benefit:** the draft addresses the governed need rather than a lossy restatement. **Priority:** P0. **Dependencies:** portfolio/control-plane contracts.  
**Acceptance:** Given complete approved canonical context, when accepted, then evidence preserves its source, identities, constraints and immutable digest; incomplete or contradictory context is rejected before generation. **Trace:** FR-INT-01.

### US-02 — Understand the supported promise
**Role:** engineering lead. **Goal:** see what project class, behavior and checks Slugger accepts and excludes. **Benefit:** I can make an informed use decision. **Priority:** P0. **Dependencies:** capability catalog.  
**Acceptance:** Scope declaration distinguishes supported/experimental behavior, promised verification, exclusions, and human responsibilities; unsupported intent fails with actionable constraints. **Trace:** FR-SCP-01, FR-CAT-01.

### US-03 — Retain approval authority
**Role:** portfolio approver. **Goal:** ensure only currently approved work executes. **Benefit:** automation cannot bypass governance. **Priority:** P0. **Dependencies:** current authority evidence.  
**Acceptance:** absent/withdrawn approval and local labels alone cause no provider invocation or target mutation. **Trace:** FR-INT-02.

## Generation, isolation, and verification

### US-04 — Protect trusted source
**Role:** maintainer. **Goal:** keep generated activity away from Slugger and protected checkouts. **Benefit:** experimentation cannot corrupt product source. **Priority:** P0. **Dependencies:** supported containment environment.  
**Acceptance:** traversal/link/source-root attempts are blocked and concurrent workspaces do not overlap. **Trace:** FR-WS-01, NFR-SEC-02.

### US-05 — Reproduce the generation request
**Role:** architect/reviewer. **Goal:** identify the exact bounded request and provider context. **Benefit:** I can understand provenance and compare attempts. **Priority:** P0. **Dependencies:** prompt policy.  
**Acceptance:** evidence contains normalized input, prompt/policy/provider identities and digest without secrets. **Trace:** FR-PRM-01, NFR-AI-03.

### US-06 — Receive observed validation
**Role:** reviewer. **Goal:** see inventory, validation, install, test and smoke evidence separately. **Benefit:** I can distinguish observed facts from AI claims. **Priority:** P0. **Dependencies:** controlled verifier.  
**Acceptance:** every result includes status/scope/evidence; a failed, skipped, errored or stale required check blocks publication. **Trace:** FR-ART-01, FR-VAL-01, FR-TST-01, FR-SMK-01.

### US-07 — Contain untrusted execution
**Role:** security authority. **Goal:** prevent generated code/dependencies from reaching secrets or protected resources. **Benefit:** AI acceleration does not create uncontrolled code execution. **Priority:** P0. **Dependencies:** containment and credential administration.  
**Acceptance:** adversarial tests show no access to publication credentials, source, state, other runs or prohibited networks; limit violation fails closed. **Trace:** FR-EXE-01, NFR-SEC-01–05.

## Publication, review, and recovery

### US-08 — Receive one reviewable draft
**Role:** maintainer. **Goal:** receive verified content in one clearly owned draft PR. **Benefit:** normal review practices remain the boundary. **Priority:** P0. **Dependencies:** GitHub/target.  
**Acceptance:** exactly one open managed draft per logical delivery, limited to verified files, contains evidence and next steps, and is never auto-approved/merged. **Trace:** FR-PUB-01/02.

### US-09 — Retry without duplicate work
**Role:** program manager/operator. **Goal:** safely redeliver or resume after interruption. **Benefit:** recovery does not multiply cost or PRs. **Priority:** P0. **Dependencies:** durable state and stable delivery identity.  
**Acceptance:** duplicate complete work is reused without generation; safe partial work resumes with revalidation; ambiguity is unchanged and escalated. **Trace:** FR-IDM-01, FR-REC-01.

### US-10 — Understand failure and next action
**Role:** operator. **Goal:** see phase, cause, impact, retryability and safe remediation. **Benefit:** I can recover efficiently without bypassing a gate. **Priority:** P0. **Dependencies:** correlated evidence.  
**Acceptance:** each representative failure is correctly categorized/redacted, retains evidence, blocks publication, and identifies its accountable owner/next action. **Trace:** FR-ERR-01, NFR-OBS-02.

### US-11 — Make the consequential decision
**Role:** reviewer/security/release authority. **Goal:** retain authority over readiness, merge, release and production. **Benefit:** accountability remains human. **Priority:** P0. **Dependencies:** target governance.  
**Acceptance:** evidence names outstanding decisions and automation cannot self-record them or advance beyond a draft. **Trace:** FR-GOV-01.

## Operations and evolution

### US-12 — Operate with safe configuration
**Role:** operator. **Goal:** validate effective limits/endpoints/policy before a run. **Benefit:** environmental mistakes fail early and are diagnosable. **Priority:** P1. **Dependencies:** deployment profile.  
**Acceptance:** invalid configuration blocks before work, precedence is deterministic, effective non-secret configuration identity is evidenced, and safe defaults apply. **Trace:** NFR-CFG-01–03.

### US-13 — Automate without hidden interaction
**Role:** automation consumer/AI agent. **Goal:** use versioned machine inputs and results non-interactively. **Benefit:** future SDLC automation is reliable and governable. **Priority:** P1. **Dependencies:** versioned contract.  
**Acceptance:** no hidden prompt occurs; result and evidence validate; exit category is deterministic; same authority rules apply to machine actor. **Trace:** NFR-AUT-01/02.

### US-14 — Substitute a provider
**Role:** architect/capability owner. **Goal:** evaluate another provider without changing governance semantics. **Benefit:** product policy is not locked to one vendor. **Priority:** P2. **Dependencies:** provider conformance suite.  
**Acceptance:** substitute passes common inputs/outputs/errors/evidence/security tests and receives no broader authority. **Trace:** FR-EXT-01.

### US-15 — Add a bounded lifecycle phase
**Role:** product owner. **Goal:** promote one independently reviewable SDLC capability. **Benefit:** Slugger expands without unsafe monolithic autonomy. **Priority:** P2. **Dependencies:** discovery and promotion gate.  
**Acceptance:** phase declares contracts, validation, evidence, compatibility, recovery and human gate; passes BR-20; existing MVP remains unaffected. **Trace:** FR-LCM-01/02.
