# Functional Requirements

## Requirement record convention

Each record is atomic at the product-behavior level. “Input” and “output” identify information, not transport or schema. Priorities: P0 MVP release-blocking; P1 MVP important; P2 post-MVP; P3 candidate. Unless stated otherwise, the precondition is an authorized actor or canonical caller and the postcondition is a durable, correlated outcome.

> **MVP interpretation:** priorities in this historical product baseline do not by themselves select the organization next MVP. The exact included and deferred IDs are defined in [the organization next-MVP contribution](../next-mvp.md#normative-repository-scope).

## A. Intent intake and scope

### FR-INT-01 — Accept complete approved intent
**Description:** Slugger MUST accept a single bounded software intent only when accompanied by canonical contract version, logical task and delivery identities, correlation and source references, target, execution mode, approval assertion, project class, publication policy, and immutable request context required by the applicable contract.  
**Rationale:** Execution must remain tied to its governance context. **Priority:** P0. **Dependencies:** external portfolio and control-plane contracts; BR-01–BR-04.  
**Inputs:** canonical execution request. **Outputs:** validated normalized request or rejection reasons. **Preconditions:** supported contract is available. **Postconditions:** accepted fields are bound to the run and immutable-input digest.  
**Acceptance:** **AC-INT-01a:** complete supported input is accepted without losing supplied context. **AC-INT-01b:** each absent, malformed, unsupported, or contradictory mandatory field blocks execution before provider invocation. **AC-INT-01c:** rejection identifies fields and does not mutate a target.  
**Vision:** VG-01, VG-02, VG-07.

### FR-INT-02 — Verify authority at execution time
**Description:** Slugger SHALL verify that the request is routed by the authorized control plane, targets registered Slugger capability, retains valid explicit execution approval, requests a permitted mode, and enforces draft-only publication before mutating execution.  
**Rationale:** Stale or local signals cannot authorize consequential action. **Priority:** P0. **Dependencies:** Interface-portfolio-tasks; Interface-organization-github.  
**Inputs:** request and current authority evidence. **Outputs:** authorization decision/evidence. **Preconditions:** request passed structural validation. **Postconditions:** unauthorized work has no generation or target mutation.  
**Acceptance:** **AC-INT-02a:** withdrawn/absent approval blocks implement mode. **AC-INT-02b:** local issue labels alone never authorize production execution. **AC-INT-02c:** verification mode causes no provider call or repository mutation.  
**Vision:** VG-03, VG-07.

### FR-SCP-01 — Bound and communicate supported scope
**Description:** Slugger MUST evaluate intent against the supported project-class catalog and disclose accepted constraints, promised checks, exclusions, and residual human responsibilities before generation.  
**Rationale:** Users must not mistake a narrow proof for broad product support. **Priority:** P0. **Dependencies:** FR-CAT-01.  
**Inputs:** intent, project class, catalog version. **Outputs:** scope decision and scope declaration. **Preconditions:** authorized request. **Postconditions:** only supported, bounded work proceeds.  
**Acceptance:** **AC-SCP-01a:** MVP accepts only the governed dependency-minimal Python CLI class. **AC-SCP-01b:** unsupported or unbounded intent is rejected with unmet constraints. **AC-SCP-01c:** the run evidence states what validation does and does not establish.  
**Vision:** VG-01, VG-03.

### FR-CAT-01 — Govern supported capability catalog
**Description:** Slugger SHALL expose an identifiable catalog of supported project classes, templates/capabilities, required inputs, promised outputs, validation profile, and lifecycle status; experimental entries MUST NOT be represented as supported.  
**Rationale:** Capability claims require a controlled source. **Priority:** P1. **Dependencies:** BR-20.  
**Inputs:** approved catalog release. **Outputs:** queryable/readable catalog identity. **Preconditions:** product release selected. **Postconditions:** run references exact applicable entry.  
**Acceptance:** **AC-CAT-01a:** catalog distinguishes supported, deprecated, and experimental. **AC-CAT-01b:** an unknown identifier fails closed. **AC-CAT-01c:** evidence records catalog entry/version.  
**Vision:** VG-02, VG-06.

## B. Run control, prompt, and provider

### FR-RUN-01 — Establish stable run and delivery identity
**Description:** Slugger MUST create a unique run identity and bind it to the contract-defined stable logical delivery identity, correlation identity, source, target, base, requested branch, and immutable-input digest. Runtime attempt IDs MUST NOT replace logical identity.  
**Rationale:** Audit and idempotency require stable correlation. **Priority:** P0. **Dependencies:** canonical contract.  
**Inputs:** validated request. **Outputs:** durable run record. **Preconditions:** request authorized. **Postconditions:** identity bindings cannot silently change.  
**Acceptance:** **AC-RUN-01a:** redelivery preserves delivery ownership while each attempt remains distinguishable. **AC-RUN-01b:** conflicting immutable input under one delivery ID blocks. **AC-RUN-01c:** all artifacts/events correlate to the run and delivery.  
**Vision:** VG-02, VG-05.

### FR-RUN-02 — Persist lifecycle state
**Description:** Slugger SHALL durably record phase status, timestamps, decisions, safe errors, evidence references, output references, retry lineage, and terminal outcome at every boundary.  
**Rationale:** Operators need recovery after interruption. **Priority:** P0. **Dependencies:** NFR-REL-03, NFR-OBS-01.  
**Inputs:** lifecycle events. **Outputs:** ordered state history. **Preconditions:** run exists. **Postconditions:** latest valid state is recoverable.  
**Acceptance:** **AC-RUN-02a:** interruption at each boundary retains the last completed phase. **AC-RUN-02b:** invalid state transition is blocked/audited. **AC-RUN-02c:** terminal success, failure, blocked, and cancelled outcomes are distinguishable where contract permits.  
**Vision:** VG-02, VG-05.

### FR-PRM-01 — Construct reproducible generation request
**Description:** Slugger MUST transform bounded intent into a constrained provider request using an identifiable prompt/policy version, preserving source intent, normalized inputs, constraints, requested output location, and provenance.  
**Rationale:** Reproducibility and review require knowing what was requested. **Priority:** P0. **Dependencies:** FR-SCP-01.  
**Inputs:** bounded intent, catalog entry, prompt policy. **Outputs:** provider-neutral request and digest. **Preconditions:** workspace ready. **Postconditions:** immutable request evidence retained subject to retention policy.  
**Acceptance:** **AC-PRM-01a:** same normalized immutable inputs and versions yield the same request digest. **AC-PRM-01b:** user content cannot override system safety/publication policy. **AC-PRM-01c:** secrets are absent/redacted from retained prompt evidence.  
**Vision:** VG-02, VG-04.

### FR-PRV-01 — Execute through a bounded provider interface
**Description:** Slugger SHALL invoke an approved generation provider only inside the assigned workspace, with phase-scoped capabilities, bounded resources, allowlisted context, and no publication authority. It MUST capture provider identity/version where available, session/correlation data, result category, and bounded diagnostics.  
**Rationale:** Provider behavior must remain subordinate to product policy. **Priority:** P0. **Dependencies:** Interface-ai-generation-provider; FR-WS-01.  
**Inputs:** provider-neutral request and workspace authorization. **Outputs:** candidate files and provider execution evidence. **Preconditions:** authorized implement mode. **Postconditions:** provider completion does not imply validation.  
**Acceptance:** **AC-PRV-01a:** unavailable/failed provider produces a failed phase, preserved safe evidence, and no fallback presented as provider output. **AC-PRV-01b:** attempted writes outside workspace are blocked. **AC-PRV-01c:** provider never receives target publication credential.  
**Vision:** VG-01, VG-04, VG-06.

## C. Isolation and generated output

### FR-WS-01 — Create isolated run workspace
**Description:** Slugger MUST create a run-specific generated-project workspace outside Slugger source, installed package locations, target production checkout, and other runs; it SHALL verify containment before use.  
**Rationale:** Generation must not corrupt trusted source. **Priority:** P0. **Dependencies:** NFR-SEC-02.  
**Inputs:** run identity and configured runtime location. **Outputs:** verified workspace reference. **Preconditions:** valid writable approved storage. **Postconditions:** generated activity is contained.  
**Acceptance:** **AC-WS-01a:** repository-root, source-subtree, absolute/traversal, and escaping-link workspaces are rejected. **AC-WS-01b:** concurrent runs cannot share writable workspace state. **AC-WS-01c:** source integrity check detects any mutation.  
**Vision:** VG-04.

### FR-WS-02 — Govern workspace retention and cleanup
**Description:** Slugger SHALL preserve or remove workspaces according to configured, disclosed retention policy; cleanup MUST verify ownership and MUST NOT follow links or remove unowned paths.  
**Rationale:** Evidence needs must be balanced with security and storage. **Priority:** P1. **Dependencies:** NFR-CFG-01; NFR-CMP-02.  
**Inputs:** terminal state, retention policy, ownership metadata. **Outputs:** retention/cleanup record. **Preconditions:** workspace ownership provable. **Postconditions:** policy applied without affecting other data.  
**Acceptance:** **AC-WS-02a:** failure evidence is available for configured diagnostic period. **AC-WS-02b:** ambiguous ownership blocks deletion. **AC-WS-02c:** cleanup is auditable.  
**Vision:** VG-02, VG-04.

### FR-ART-01 — Inventory and protect candidate artifacts
**Description:** Slugger MUST produce a complete generated-file inventory containing normalized relative identity, type, size, integrity digest, provenance phase, and policy disposition; protected evidence MUST be separated from provider-writable output.  
**Rationale:** Review and tamper detection require a trustworthy bill of generated artifacts. **Priority:** P0. **Dependencies:** FR-WS-01.  
**Inputs:** candidate workspace. **Outputs:** protected manifest and digest. **Preconditions:** provider phase ended. **Postconditions:** downstream phases use the recorded candidate set.  
**Acceptance:** **AC-ART-01a:** added, removed, changed, duplicate-normalized, and escaping paths are detected. **AC-ART-01b:** later candidate mutation invalidates prior evidence. **AC-ART-01c:** manifest cannot be overwritten by generated code.  
**Vision:** VG-02, VG-04.

## D. Validation and verification

### FR-VAL-01 — Validate output before execution
**Description:** Slugger MUST evaluate every candidate against the selected project's path, file, size, content, language syntax, naming, structure, packaging, dependency, secret, and prohibited-behavior policies before installation or generated execution.  
**Rationale:** Unsafe output must be rejected before it can act. **Priority:** P0. **Dependencies:** FR-CAT-01, FR-ART-01.  
**Inputs:** protected manifest, candidate files, validation profile. **Outputs:** per-check results and aggregate gate. **Preconditions:** stable inventory. **Postconditions:** only passing output may install.  
**Acceptance:** **AC-VAL-01a:** one required failed/error/incomplete check blocks later execution and publication. **AC-VAL-01b:** check evidence identifies policy/version and affected artifact without exposing secrets. **AC-VAL-01c:** symlinks, special files, path ambiguity, embedded credentials, and disallowed dependencies fail closed.  
**Vision:** VG-01, VG-02, VG-04.

### FR-DEP-01 — Control dependency acquisition
**Description:** Slugger SHALL resolve and acquire only dependencies permitted by the applicable project profile and environment policy, record source/provenance and resolved identity, and fail closed when integrity, availability, or policy cannot be established.  
**Rationale:** Dependencies are an untrusted execution boundary. **Priority:** P0. **Dependencies:** FR-VAL-01; NFR-SEC-04.  
**Inputs:** declared dependencies and approved source policy. **Outputs:** resolution evidence or rejection. **Preconditions:** validation passed. **Postconditions:** only admitted dependencies enter execution environment.  
**Acceptance:** **AC-DEP-01a:** undeclared/disallowed sources and dependencies block. **AC-DEP-01b:** resolution is bounded and recorded. **AC-DEP-01c:** dependency failure cannot be reported as a project test failure or success.  
**Vision:** VG-02, VG-04.

### FR-EXE-01 — Install and execute in controlled isolation
**Description:** Slugger MUST install and run generated software in a fresh project-specific environment separated from Slugger, other runs, credentials, and protected host resources, with bounded time, output, processes, storage, and network access according to policy.  
**Rationale:** Candidate code is untrusted. **Priority:** P0. **Dependencies:** FR-DEP-01; NFR-SEC-02.  
**Inputs:** validated candidate and admitted dependencies. **Outputs:** installation/execution evidence. **Preconditions:** all pre-execution gates pass. **Postconditions:** environment cannot be promoted or reused as trusted production state.  
**Acceptance:** **AC-EXE-01a:** generated processes cannot access publication secrets or Slugger state. **AC-EXE-01b:** limit violation terminates the phase and blocks publication. **AC-EXE-01c:** installation result is distinct from test/smoke results.  
**Vision:** VG-04.

### FR-TST-01 — Execute bounded automated tests
**Description:** Slugger SHALL discover/select tests according to the project-class profile, execute them in isolation, and retain commands/criteria, environment identity, duration, exit category, bounded output, and test counts where available.  
**Rationale:** Reviewers require observed behavioral evidence. **Priority:** P0. **Dependencies:** FR-EXE-01.  
**Inputs:** installed candidate, test profile. **Outputs:** test evidence and gate. **Preconditions:** installation passed. **Postconditions:** a required test failure blocks publication.  
**Acceptance:** **AC-TST-01a:** no required tests, test failure, timeout, crash, or ambiguous runner result fails the required gate. **AC-TST-01b:** generated claims cannot substitute for observed result. **AC-TST-01c:** evidence distinguishes pass/fail/error/not-run.  
**Vision:** VG-01, VG-02.

### FR-SMK-01 — Perform deterministic smoke verification
**Description:** Slugger MUST execute the project-class minimum promised behavior using predefined, non-interactive inputs and compare exit behavior and normalized observable output with explicit expectations.  
**Rationale:** Tests alone do not establish that the delivered interface starts and responds. **Priority:** P0. **Dependencies:** FR-TST-01.  
**Inputs:** installed candidate and smoke profile. **Outputs:** invocation, expected/observed comparison, gate result. **Preconditions:** required tests pass. **Postconditions:** mismatch blocks publication.  
**Acceptance:** **AC-SMK-01a:** repeated checks in equivalent declared environments produce the same normalized verdict. **AC-SMK-01b:** timeout, prompt-for-input, unexpected side effect, exit mismatch, or output mismatch fails. **AC-SMK-01c:** scope of proven behavior is stated.  
**Vision:** VG-01, VG-02, VG-05.

### FR-EVD-01 — Assemble review evidence
**Description:** Slugger SHALL assemble an integrity-protected evidence package linking approved input, scope, identities, prompt provenance, artifact manifest, provider result, every gate, environment, status history, publication, known exclusions, and residual human decisions.  
**Rationale:** Evidence is the product's basis for trust. **Priority:** P0. **Dependencies:** all run phases.  
**Inputs:** phase records. **Outputs:** human-readable summary and machine-readable evidence. **Preconditions:** terminal or blocked point reached. **Postconditions:** facts, claims, failures, skipped checks, and unknowns remain distinguishable.  
**Acceptance:** **AC-EVD-01a:** integrity alteration is detectable. **AC-EVD-01b:** summary links each claim to observed evidence. **AC-EVD-01c:** secrets/sensitive values are excluded or redacted. **AC-EVD-01d:** partial runs produce truthful partial evidence, never a passing aggregate.  
**Vision:** VG-02, VG-03.

## E. Publication, retry, and recovery

### FR-PUB-01 — Gate publication
**Description:** Slugger MUST permit publication only for an authorized implement request whose required validation, dependency, installation, test, smoke, manifest-integrity, source-integrity, and target-preflight gates all pass and whose evidence remains current.  
**Rationale:** Publication is consequential. **Priority:** P0. **Dependencies:** FR-EVD-01; BR-11.  
**Inputs:** gate/evidence set and current authority. **Outputs:** publication authorization decision. **Preconditions:** candidate is stable. **Postconditions:** any ambiguity/failed/incomplete/stale gate blocks mutation.  
**Acceptance:** **AC-PUB-01a:** a fault injected into each gate independently yields no push or PR creation/update. **AC-PUB-01b:** approval withdrawal before mutation blocks. **AC-PUB-01c:** successful decision records exact evidence digest.  
**Vision:** VG-01, VG-03, VG-04.

### FR-PUB-02 — Publish one managed draft review
**Description:** Slugger SHALL publish only inventoried verified files and review evidence to the contract-defined deterministic branch/base and create or update at most one demonstrably Slugger-owned open draft pull request per logical delivery. It SHALL NOT approve, mark ready, merge, release, deploy, or close work.  
**Rationale:** A draft PR is the automation/human boundary. **Priority:** P0. **Dependencies:** Interface-github-platform; target interface.  
**Inputs:** authorized publication, target, branch, verified artifacts, ownership marker. **Outputs:** branch/commit/draft PR references. **Preconditions:** ownership and permissions unambiguous. **Postconditions:** target contains a reviewable draft tied to evidence.  
**Acceptance:** **AC-PUB-02a:** PR is draft and identifies source/delivery/correlation, scope, checks, evidence and human next steps. **AC-PUB-02b:** unverified/stale/provider-control files are absent. **AC-PUB-02c:** automation cannot merge or approve. **AC-PUB-02d:** target changes are limited to the owned branch/draft.  
**Vision:** VG-02, VG-03, VG-07.

### FR-IDM-01 — Make redelivery and publication idempotent
**Description:** Slugger MUST classify durable target state before provider invocation and before publication. Completed matching delivery SHALL be reused; an absent delivery MAY proceed; conflicting, ambiguous, unowned, non-draft, closed/merged, wrong-base, or multiply matching state MUST be preserved and fail closed.  
**Rationale:** At-least-once delivery must not duplicate or overwrite work. **Priority:** P0. **Dependencies:** FR-RUN-01, FR-PUB-02.  
**Inputs:** stable delivery identity, expected ownership and target state. **Outputs:** proceed/reuse/block classification. **Preconditions:** read access to target. **Postconditions:** no guessing or destructive reconciliation.  
**Acceptance:** **AC-IDM-01a:** sequential and concurrent identical deliveries result in at most one managed open draft. **AC-IDM-01b:** completed matching delivery does not reinvoke provider. **AC-IDM-01c:** every unsafe state is unchanged and accompanied by recovery guidance. **AC-IDM-01d:** runtime IDs/timestamps/randomness do not determine ownership.  
**Vision:** VG-05.

### FR-REC-01 — Resume or retry safely
**Description:** Slugger SHALL support policy-permitted resume/retry from the last trustworthy boundary, revalidate mutable authority, environment, artifact integrity, and target state, and rerun any stale dependent checks.  
**Rationale:** Recovery must not bypass gates. **Priority:** P1. **Dependencies:** FR-RUN-02, FR-IDM-01.  
**Inputs:** run/delivery identity and recovery request. **Outputs:** resumed attempt or actionable refusal. **Preconditions:** retained state is readable and ownership proven. **Postconditions:** retry lineage and revalidation recorded.  
**Acceptance:** **AC-REC-01a:** interruption scenarios resume without treating partial phase as passed. **AC-REC-01b:** changed candidate invalidates downstream evidence. **AC-REC-01c:** irrecoverable/ambiguous state is preserved for human action.  
**Vision:** VG-05.

### FR-ERR-01 — Provide actionable failure outcomes
**Description:** Every rejected, failed, timed-out, blocked, or interrupted phase SHALL produce a safe categorized outcome with phase, cause, impact, retryability, evidence location, and authorized next action; internal/provider assertions MUST NOT be exposed as verified facts.  
**Rationale:** Users need recovery without unsafe bypasses. **Priority:** P0. **Dependencies:** NFR-OBS-*.  
**Inputs:** exception, timeout, validation failure, external failure. **Outputs:** safe failure record and user summary. **Preconditions:** run or intake attempt exists. **Postconditions:** publication remains blocked unless all gates later pass.  
**Acceptance:** **AC-ERR-01a:** representative failures yield distinct category and next step. **AC-ERR-01b:** secrets and unsafe raw content are not disclosed. **AC-ERR-01c:** no failure is represented as success or production readiness.  
**Vision:** VG-02, VG-05.

## F. Organization contract and continuous conformance

### FR-RES-01 — Produce and expose the canonical execution result
**Description:** Slugger MUST map every terminal, rejected, failed, reused, no-change, interrupted, or ambiguous local observation to the pinned organization-owned execution-result contract, validate it with the official validator, durably retain it, and deliver or expose it through the approved mechanism with at-least-once-safe identity. Slugger SHALL NOT define substitute schema or status semantics.
**Rationale:** Routing is incomplete without a truthful, correlated, interoperable outcome. **Priority:** organization next-MVP P0. **Dependencies:** external result contract and transport decision; FR-RUN-01; FR-EVD-01.
**Acceptance:** **AC-RES-01a:** verify success, implement success, existing-draft reuse, no change, authorization rejection, contract rejection, execution failure, validation failure, publication failure, and ambiguous/interrupted execution each produce a validator-accepted result. **AC-RES-01b:** required version; delivery, correlation and target identities; canonical status; validation evidence; applicable draft metadata; safe error; timestamps; and retry/reconciliation guidance survive mapping. **AC-RES-01c:** unknown required status/field or uncertain result delivery fails closed and is reconciled without changing execution truth or duplicating a visible effect.

### FR-CNF-01 — Continuously prove target-interface conformance
**Description:** Slugger MUST provide a deterministic, merge-blocking, no-Codex CI suite against immutably pinned organization fixtures and official validators, using fakes for authority, executor, repository, publication, clock, and result delivery.
**Rationale:** Interface drift must be found without credentials or organization mutations. **Priority:** organization next-MVP P0. **Dependencies:** shared fixture release and pinning decision.
**Acceptance:** **AC-CNF-01a:** valid verify and implement, deterministic change/no-change, simulated publication, managed-draft reuse, duplicate delivery, invalid target, invalid/withdrawn/stale approval, unsupported version, malformed request, validation failure, and every required result class are exercised. **AC-CNF-01b:** Codex credentials are absent, Codex network calls are trapped, and no real branch/commit/push/PR is created. **AC-CNF-01c:** fixture/validator incompatibility fails the required check and blocks merge; local fixtures cannot redefine canonical semantics.

## G. Human governance and lifecycle evolution

### FR-GOV-01 — Preserve human decision gates
**Description:** Slugger SHALL identify the accountable human role and required decision at intent approval, material scope/architecture exception, security disposition, draft review, merge, release, deployment, and production use; it MUST NOT self-satisfy those gates.  
**Rationale:** AI augments rather than replaces accountable judgment. **Priority:** P0. **Dependencies:** BR-01, BR-14.  
**Inputs:** governance state and evidence. **Outputs:** pending/recorded decision reference. **Preconditions:** applicable lifecycle point. **Postconditions:** consequential progression requires external human decision.  
**Acceptance:** **AC-GOV-01a:** generated/provider content cannot create valid human approval. **AC-GOV-01b:** evidence names outstanding decisions. **AC-GOV-01c:** merge/release/deployment are never performed by Slugger automation.  
**Vision:** VG-03.

### FR-LCM-01 — Manage lifecycle artifacts (post-MVP)
**Description:** Slugger SHALL identify, version, relate, review-state, retain, and hand off professional lifecycle artifacts with provenance and explicit upstream/downstream traceability.  
**Rationale:** Long-term value requires fidelity across phases. **Priority:** P2. **Dependencies:** approved phase-specific requirements.  
**Inputs:** approved artifact and predecessor references. **Outputs:** versioned artifact, relationships, review state. **Preconditions:** capability has passed promotion. **Postconditions:** supersession never erases history.  
**Acceptance:** **AC-LCM-01a:** each artifact identifies origin, version, status, owner, inputs and successors. **AC-LCM-01b:** changed upstream artifact identifies potentially impacted downstream artifacts. **AC-LCM-01c:** unapproved draft is not treated as approved phase input.  
**Vision:** VG-02, VG-06.

### FR-LCM-02 — Compose bounded lifecycle capabilities (post-MVP)
**Description:** Each promoted lifecycle capability SHALL declare versioned inputs, outputs, validation, evidence, authority, failure behavior, compatibility, pause/resume semantics, and named human review point; orchestration MUST permit independent replacement and MUST NOT grant unrestricted autonomous authority.  
**Rationale:** Safe expansion requires explicit seams. **Priority:** P2. **Dependencies:** FR-LCM-01, BR-20.  
**Inputs:** approved capability definitions and artifacts. **Outputs:** governed phase result. **Preconditions:** compatibility and required approval satisfied. **Postconditions:** result is independently reviewable.  
**Acceptance:** **AC-LCM-02a:** missing/incompatible input blocks only dependent phase. **AC-LCM-02b:** phase can be paused, resumed, replaced, and independently audited. **AC-LCM-02c:** no composition bypasses review gates.  
**Vision:** VG-03, VG-06.

### FR-EXT-01 — Support replaceable providers/extensions
**Description:** Slugger SHALL evaluate a provider or extension against a provider-neutral capability contract covering inputs, outputs, errors, evidence, security, resource controls, and compatibility before activation; extensions MUST NOT override product policy or human authority.  
**Rationale:** Product semantics must not depend on one vendor. **Priority:** P2 (contract is P1). **Dependencies:** NFR-INT-01.  
**Inputs:** capability declaration and conformance evidence. **Outputs:** approved/unsupported decision. **Preconditions:** extension is identifiable/versioned. **Postconditions:** run records selected provider/capability.  
**Acceptance:** **AC-EXT-01a:** missing mandatory capability yields preflight rejection. **AC-EXT-01b:** equivalent result/error/evidence semantics are testable with a substitute. **AC-EXT-01c:** extension cannot receive broader authority than phase requires.  
**Vision:** VG-04, VG-06.
