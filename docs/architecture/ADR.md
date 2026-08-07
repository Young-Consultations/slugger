# Architectural Decision Records

**Status:** This consolidated decision register supersedes prior implementation-oriented ADRs. Decisions govern future implementation; open questions do not grant permission.

## ADR-001 — One governed supported pipeline

**Context:** Equivalent entry points and duplicate experimental paths can produce inconsistent authority and gates.
**Decision:** All supported requests normalize into one application process manager and domain policy sequence. Inbound workflows/CLI are adapters only.
**Alternatives:** Separate workflows per channel; provider-led orchestration.
**Tradeoffs:** Less channel customization; materially stronger consistency and testability.
**Consequences:** BR-25 conformance is testable; adapters cannot own business gates.
**Open questions:** Which existing entry points remain during migration and for how long?

## ADR-002 — Clean/hexagonal modular monolith first

**Context:** Strong boundaries are required, while scale and deployment facts do not justify distributed complexity.
**Decision:** Domain/application center with ports/adapters, composed initially as a modular monolith; logical boundaries are deployment-independent.
**Alternatives:** Microservices now; workflow scripts as architecture; layered infrastructure-first application.
**Tradeoffs:** Requires disciplined dependency tests; avoids premature network consistency/operations cost.
**Consequences:** Components may split later behind unchanged ports.
**Open questions:** What measured threshold justifies splitting verification or provider workers?

## ADR-003 — Persisted process manager and explicit state machine

**Context:** Long-running external calls, interruption and at-least-once delivery require recoverability.
**Decision:** A single run coordinator advances an explicit persisted state machine with append-only history, optimistic versioning, operation intents and reconciliation.
**Alternatives:** In-memory pipeline; CI job state; general event choreography.
**Tradeoffs:** More lifecycle modeling and migrations; truthful recovery and fault injection.
**Consequences:** Workflow run IDs are operational metadata only.
**Open questions:** Approved durability/availability/retention objectives.

## ADR-004 — Candidate content is hostile until independently verified

**Context:** AI output and dependencies can be malicious or incorrect.
**Decision:** Contain, normalize, inventory, hash and statically admit before execution; execute only in controlled isolation with no publication authority.
**Alternatives:** Trust provider formatting; execute then scan.
**Tradeoffs:** Restricts generated projects and costs verifier resources; prevents uncontrolled behavior.
**Consequences:** Candidate/project-class profiles define allowed output and commands.
**Open questions:** Approved isolation technology and egress strength per deployment.

## ADR-005 — Capability profiles are the unit of supported evolution

**Context:** Code presence must not imply support.
**Decision:** A versioned profile binds project class/mode, promises, limits, policies, verifier, contracts, evidence and human gate; only BR-20-promoted profiles are supported.
**Alternatives:** Feature flags; dynamic plugin discovery as support.
**Tradeoffs:** Promotion is slower; scope and assurance are explicit.
**Consequences:** MVP Python CLI profile remains the only committed class.
**Open questions:** Promotion board membership and quantitative targets.

## ADR-006 — Integrity-bound evidence is a first-class domain output

**Context:** Logs and provider claims cannot support accountable review or safe reuse.
**Decision:** Assemble immutable human/machine evidence bound to request, candidate, policy, config, tools, environment and observations; audit transitions separately.
**Alternatives:** Console logs; PR description only.
**Tradeoffs:** Storage/access/retention complexity; reliable traceability and stale detection.
**Consequences:** Evidence write/seal failure blocks publication.
**Open questions:** Retention, signing and classification policy.

## ADR-007 — Logical delivery owns idempotent draft publication

**Context:** Redelivery/concurrency and GitHub races can duplicate or overwrite work.
**Decision:** Canonical delivery/publication identity—not run/attempt/time—binds deterministic branch and versioned marker. Reconcile structurally and mutate only one proven managed open draft.
**Alternatives:** Random branch per run; name-prefix ownership; force reconciliation.
**Tradeoffs:** Conservative human blocks in ambiguous cases; avoids destructive action.
**Consequences:** Exact completion is reused without provider reinvocation.
**Open questions:** Canonical future identity migration and approved legacy-marker window.

## ADR-008 — Separate authority and credentials by phase

**Context:** Generated behavior must never obtain publication or provider secrets.
**Decision:** Broker least-privilege, short-lived credentials to the component/phase that needs them; generation, verification and publication are distinct trust zones.
**Alternatives:** One job token/environment; environment variables inherited by children.
**Tradeoffs:** More operational identity configuration; reduced blast radius.
**Consequences:** Generated sandbox receives no provider/publication credential.
**Open questions:** Credential authority and emergency revocation mechanism.

## ADR-009 — External contracts remain externally owned

**Context:** Sibling implementations are unavailable and local schema copies drift.
**Decision:** Pin trusted releases/validators and map through adapters; store attributed references/snapshots; unknown major/semantics fail closed.
**Alternatives:** Copy schema/enums; infer fields from workflows.
**Tradeoffs:** External availability/version coordination; preserves ownership.
**Consequences:** Verification-only until integration conformance is approved.
**Open questions:** Distribution trust, rollout order, result transport and compatibility window.

## ADR-010 — Experimental capabilities are quarantined

**Context:** Repository research components could accidentally expand product claims or dependencies.
**Decision:** Supported code has no dependency on experimental paths; experimental results are visibly nonconformant with supported evidence; promotion follows ADR-005.
**Alternatives:** Maintain both as equivalent; delete all research immediately.
**Tradeoffs:** Temporary duplication may remain; MVP stays independently replaceable.
**Consequences:** Architecture/dependency tests enforce the boundary.
**Open questions:** Retain, extract or remove inventory and deadlines.

## ADR-011 — Typed failures and no implicit pass

**Context:** Boolean/error flattening hides uncertainty and encourages unsafe retry.
**Decision:** Owned error taxonomy and multi-state gates; only fresh explicit PASS progresses. Ports return typed outcomes with safe detail references.
**Alternatives:** Exceptions/exit codes only; best-effort progression.
**Tradeoffs:** More modeling; consistent recovery and truthful UX.
**Consequences:** Skip/timeout/error/stale/unknown deny dependent action.
**Open questions:** Canonical external mapping vocabulary.

## ADR-012 — Observability is distinct from evidence

**Context:** Telemetry may be unavailable, sampled or externally exported, while evidence is mandatory and sensitive.
**Decision:** Durable local audit/evidence drives lifecycle; sanitized logs/metrics/traces support operations but never authorize progression.
**Alternatives:** Derive evidence from logs; require external APM.
**Tradeoffs:** Two intentionally related data products; correct security/availability semantics.
**Consequences:** Telemetry outage cannot fabricate or erase run truth.
**Open questions:** Deployment-specific sinks, SLOs and sampling.

## ADR-013 — Stable external approval evidence, not repository labels

**Context:** Portfolio approval truth and control-plane routing are externally owned; mutable repository labels create time-of-check races and a second authority.
**Decision:** Slugger validates pinned-contract evidence bound to issuer, task revision, target, mode and delivery, including contract-defined freshness and withdrawal/revocation rules, before Codex and again before mutation. A local label is non-authoritative unless the external contract explicitly assigns its validation to Slugger. Unknown or unavailable authority fails closed.
**Consequences:** The observed `ai-sdlc-approved` implementation check is blueprint drift pending an organization decision. Slugger neither approves tasks nor defines portfolio status transitions.
**Open questions:** Proof format/issuer, freshness and clock skew, edit/withdrawal/revocation semantics, and outage behavior.

## ADR-014 — Hermetic conformance gates external-interface changes

**Context:** Real Codex and GitHub effects are unsafe, nondeterministic, and credential-dependent in normal CI.
**Decision:** A merge-blocking suite uses immutably pinned official validators/shared fixtures and deterministic authority, executor, repository, publisher, clock, and result-sink fakes. Network/Codex and real GitHub mutations are prohibited.
**Consequences:** Contract/lifecycle drift blocks merge; credentialed demonstrations remain separate and non-normative. Local fixtures may extend but not redefine the external contract.
**Open questions:** Fixture release/digest, required check name, update cadence and compatibility window.
