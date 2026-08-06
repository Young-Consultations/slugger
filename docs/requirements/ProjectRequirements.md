# High-Level Project Requirements

## Vision and mission

**Vision.** Slugger is the governed AI Software Factory within a wider AI-assisted software-delivery operating system. It transforms approved human intent into validated, traceable, reviewable software while preserving professional judgment and human authority.

**Mission.** Reduce the effort and fidelity loss between bounded software intent and working project drafts by applying controlled generation, isolation, verification, evidence capture, and draft-only review handoff. Slugger is the execution and product-generation product; it is not the portfolio-management product. The prompt's reference to describing `portfolio-tasks` as the product conflicts with the authoritative vision and is therefore treated as external-system context, not Slugger's mission.

## Business objectives and product goals

| ID | Objective | Product outcome | Measure |
| --- | --- | --- | --- |
| BO-01 | Shorten the path from approved idea to reviewable project | A professional user receives a runnable constrained project draft | Median approved-intent-to-draft duration and manual effort, baselined before target setting |
| BO-02 | Preserve trust and accountability | Every run exposes provenance, status, checks, and human decision points | 100% of supported runs have a correlated record and terminal status |
| BO-03 | Prevent unsafe or unverified publication | Failed or incomplete gates cannot publish | 0 publications after a required gate failure in release acceptance tests |
| BO-04 | Enable safe repetition and recovery | A logical request can be retried without uncontrolled duplicate work | 100% of retry/idempotency conformance scenarios produce at most one managed open draft |
| BO-05 | Maintain organizational separation of duties | Portfolio approval, routing, execution, review, and merge remain distinct | 100% of contract conformance checks preserve assigned ownership |
| BO-06 | Expand the SDLC responsibly | New phases/classes are introduced as bounded, evidenced capabilities | Every promoted capability meets its approved promotion gate |

### Product goals

* **VG-01 — Governed transformation:** turn approved, bounded intent into verified project artifacts.
* **VG-02 — Traceability and evidence:** make inputs, transformations, outputs, checks, and decisions reviewable.
* **VG-03 — Human authority:** reserve approval, architecture accountability, security judgment, merge, release, and production use for people.
* **VG-04 — Safe isolation:** contain generated files and all untrusted installation or execution.
* **VG-05 — Reliable recovery:** provide deterministic identity, durable state, actionable failures, resume, and retry.
* **VG-06 — Composable evolution:** grow from a Python CLI proving path to bounded lifecycle capabilities without a monolithic autonomous agent.
* **VG-07 — Clear organizational boundary:** consume approved work without owning portfolio governance or organization routing.

## Target users and stakeholders

| Group | Needs / interest |
| --- | --- |
| Engineering leads | Faster project initiation, inspectable evidence, enforceable engineering gates, control over consequential decisions |
| Program managers | Predictable status, correlation to approved work, failures that can be governed and recovered |
| Technical consultants | Repeatable delivery practices, client-safe evidence, reusable but controlled lifecycle capabilities |
| Architects | Explicit constraints, traceable decisions, provider independence, promotion gates |
| Small engineering teams | Low-friction generation with clear review and ownership boundaries |
| Technically capable product owners | Faithful transformation of approved intent and understandable outcomes |
| Security/release authorities | Least privilege, containment, provenance, no implied production readiness |
| Reviewers/maintainers | Focused draft changes, verification evidence, clear residual risk and ownership |
| Organization control-plane and portfolio owners | Contract conformance and preservation of repository responsibilities |
| Operators/support | Correlated diagnostics, safe retry, retention and recovery procedures |

Generated-application end users are indirect stakeholders, not Slugger's primary persona.

## Business value

Slugger creates value by reducing repetitive setup and verification effort, retaining intent fidelity, exposing evidence rather than unverifiable AI claims, and turning generation into a reviewable engineering transaction. It reduces duplicate publication and recovery cost while enabling independent evolution of organizational repositories through explicit contracts.

## Scope

### MVP (committed boundary)

* Accept complete approved context for one bounded, dependency-minimal Python CLI project.
* Confirm supported scope and reject unsafe, incomplete, ambiguous, or unsupported requests.
* Create a run identity and isolated generated-project workspace.
* Construct and retain a versioned, constrained generation request.
* Invoke a controlled AI generation provider and capture its result without treating claims as evidence.
* Inventory output and enforce path, content, structure, language, package, and dependency policy before execution.
* Install and execute generated output only in controlled isolation.
* run automated project tests and a deterministic minimum-behavior smoke check.
* Persist status, provenance, manifests, integrity data, decisions, results, and safe diagnostics.
* Publish verified output to a deterministic branch and one Slugger-managed draft pull request.
* Support idempotent redelivery and safe, evidence-preserving recovery.
* Support a non-mutating contract-verification mode.

### Post-MVP direction

Additional project classes and professional SDLC phases from vision through maintenance MAY be promoted one bounded capability at a time. Each requires separately approved requirements, explicit versioned handoffs, isolation appropriate to risk, validation, retained evidence, compatibility rules, and a named human review gate.

## Out of scope

Slugger SHALL NOT autonomously prioritize portfolio work, approve intent or execution, own organization routing or canonical contracts, silently modify production repositories, merge or approve its own output, make production-readiness claims from narrow checks, replace accountable product/architecture/security/review roles, or support every application type in the MVP. Portfolio backlog management and issue-governance workflows belong to `portfolio-tasks`; reusable consulting content belongs to `consulting-playbook`; organization registration and routing belong to `Young-Consultations/.github`.

## Success criteria

The MVP is acceptable when all P0 requirements pass; every supported run has correlated input/output/status evidence; all prohibited publication scenarios are blocked; generated work cannot mutate Slugger's source; required tests and smoke behavior are reproducible in the declared verification environment; redelivery and publication races converge safely or fail closed; reviewers can distinguish verified facts, provider claims, skipped checks, and residual risk; and a human must act before merge or production use.

Product outcome targets beyond correctness—time saved, completion rate, reviewer comprehension, and recovery effort—SHALL be baselined through representative-user research before numeric release targets are approved (OQ-01).

## Product principles

1. Begin with approved, complete, bounded intent.
2. Evidence observed behavior; never elevate an AI assertion to verified fact.
3. Isolate generated work from product source and protected systems.
4. Validate before installing; verify before publishing.
5. Fail closed on ambiguity, unsafe state, missing authority, or incomplete evidence.
6. Automate only through a draft review boundary; retain human authority.
7. Make logical identity stable and retries safe.
8. Keep the supported path distinct from experimental capabilities.
9. Keep providers replaceable and organizational contracts explicit and versioned.
10. Expand only after the narrower capability is reliable and governed.

## Constraints

* The initial project class is a dependency-minimal Python CLI.
* GitHub is the organizational system of record and a draft pull request is the automation boundary.
* Slugger has read-only access to external repository information except for explicitly authorized draft-publication actions.
* Generated code is untrusted and SHALL never receive publication credentials.
* Cross-repository work requires complete, canonical, versioned context; local labels are not execution authority.
* The MVP supported path SHALL remain independent of experimental full-SDLC components.
* Credentials SHALL be phase-scoped, least-privileged, and non-retained.

## Assumptions, risks, and dependencies

Confirmed and working assumptions are controlled in [Assumptions.md](Assumptions.md). Principal risks are: prompt injection or malicious output; dependency or build compromise; credential leakage; duplicate/incorrect publication; weak verification being misread as production readiness; contract drift; provider unavailability; evidence confidentiality; loss of run state; and premature promotion of experimental code. Mitigating requirements are NFR-SEC-*, NFR-REL-*, NFR-OBS-*, FR-VAL-*, FR-PUB-*, and FR-GOV-*.

External dependencies are the portfolio work authority, organization contract/router, GitHub service, authorized publication repository, generation provider, dependency sources admitted by policy, identity/credential administration, and human reviewers. Their contracts and unresolved validation needs are documented in the interface documents.
