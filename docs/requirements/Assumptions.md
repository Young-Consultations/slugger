# Assumptions and Open Questions

Assumptions are not requirements and do not prove external behavior. **Confirmed** means confirmed by the authoritative Slugger vision/repository context, not by inspecting external repositories. Working assumptions require validation before the affected production decision.

## Confirmed assumptions

| ID | Assumption | Consequence |
| --- | --- | --- |
| CA-01 | Slugger, not `portfolio-tasks`, is the AI Software Factory product in this repository. | Requirements center governed execution; portfolio is an external interface. |
| CA-02 | `portfolio-tasks` owns structured intake, portfolio governance, priority and explicit execution approval. | Slugger consumes rather than invents these decisions. |
| CA-03 | Organization `.github` owns canonical contracts, routing, registration, compatibility and control-plane verification. | Slugger cannot define or activate the organization registry locally. |
| CA-04 | GitHub is the organization system of record and draft PR is the automation boundary. | Publication requirements stop before ready/merge/release. |
| CA-05 | MVP scope is a bounded dependency-minimal Python CLI and broader full-SDLC content is experimental. | Other classes/phases require promotion. |
| CA-06 | Human authority remains for intent, architecture, security, review, merge, release, deployment and production use. | No automated self-approval or production-readiness shortcut. |
| CA-07 | Cross-repository delivery is versioned, complete-context, and at least once. | Stable identity and fail-closed idempotency are mandatory. |
| CA-08 | Generated output is untrusted and activity must be isolated from Slugger source. | Pre-execution validation and containment are release gates. |

## Working assumptions

| ID | Assumption | Validation / decision impact |
| --- | --- | --- |
| WA-01 | Primary users value constrained reliability/control over broad autonomy. | Interview representative personas; affects sequencing and outcome targets. |
| WA-02 | Draft PRs provide sufficient context, access separation and feedback for target users. | Workflow usability study; may require a better review presentation while preserving human boundary. |
| WA-03 | Python CLI exercises enough factory boundaries to generalize learning. | Compare at least two candidate future classes; avoid overgeneralizing packaging/smoke rules. |
| WA-04 | A provider-neutral contract can keep Codex replaceable. | Evaluate Codex and one hypothetical/real substitute against common semantics. |
| WA-05 | Target operating environments can contain malicious generated dependencies/builds/tests to required security level. | Threat model and adversarial prototype; affected environment cannot be supported if not. |
| WA-06 | Users need retained prompt, manifest, checks and provenance and can govern their confidentiality. | Observe review/recovery and classify data; set retention/access policy. |
| WA-07 | Lifecycle phases can be composed rather than centralized into one agent. | Model representative lifecycle journeys and replacement/pause/resume behavior. |
| WA-08 | The named generated-demos repository is an appropriate sandbox target. | External owner must approve target policy and protections. |
| WA-09 | Stable identities and result semantics required by this baseline can be represented by the next approved canonical contract. | Contract-owner conformance review; activation blocked if not. |

## Unknowns

| ID | Unknown | Required discovery / owner |
| --- | --- | --- |
| OQ-01 | Baseline and targets for elapsed time, manual effort, completion rate and reviewer comprehension beyond specified quality floors | Product research with representative primary users |
| OQ-02 | Exact approved-intent completeness, approval expiry/withdrawal and material-change semantics | Portfolio and organization contract owners |
| OQ-03 | Canonical contract versions, schemas, status/failure vocabularies, registry state and compatibility window at production activation | Organization control-plane owner |
| OQ-04 | Router transport, authentication, delivery ordering, retry/backoff, result return and dead-letter/escalation behavior | Organization control-plane owner |
| OQ-05 | Supported OS/container/runtime and the enforceable filesystem/process/network containment profile | Architecture and security authorities |
| OQ-06 | Provider interface, model/version pinning, data use/residency, availability, cancellation, rate/cost limits and evidence | Provider owner, security/legal/procurement |
| OQ-07 | Allowed Python dependency sources, integrity mechanism, licensing and offline/egress policy | Security, legal and engineering |
| OQ-08 | Target repository base/protection, ownership-marker policy, allowed content, review/cleanup and incident recovery | Target repository owner |
| OQ-09 | Credential issuer, token type/lifetime/scope, rotation and emergency revocation | Security/platform owner |
| OQ-10 | Data classification, evidence/log retention, encryption, access, export/deletion, privacy jurisdictions and client confidentiality | Security, privacy/legal, records owner |
| OQ-11 | Supported input/file/size/resource ceilings and default end-to-end timeout/cost budget | Product, architecture and operations |
| OQ-12 | Recovery operator roles, backup topology and whether RPO/RTO targets need stricter deployment profiles | Operations/business owner |
| OQ-13 | Accessibility and UX delivery surface beyond CLI/PR artifacts | Product/UX and representative users |
| OQ-14 | Promotion priority and promised behavior for the first post-MVP project class or lifecycle phase | Product discovery; no inference from experimental code |
| OQ-15 | Consulting-playbook authoritative format, license, classification and approved integration use case | Consulting repository owner |
| OQ-16 | Ownership and migration/disposition of experimental full-SDLC repository content | Slugger product/architecture owner |

## Questions requiring clarification

1. What user segment and scenario is the MVP release explicitly optimized for, and what measured improvement makes it valuable?
2. What fields constitute an immutable approved work revision, and when must a new delivery identity be issued?
3. Can approval be revalidated when the source system is unavailable, or must work always block?
4. Which containment controls are mandatory across local CLI and hosted jobs, and which environments can honestly support them?
5. Which dependency classes are “dependency-minimal,” and are build/test-only dependencies permitted?
6. What minimum CLI smoke promise applies generically without inventing a generated application's domain behavior?
7. Which evidence is safe for PR presentation versus restricted operator storage, and for how long?
8. Who can resolve ambiguous target ownership and how is resolution attested before retry?
9. Must result delivery update an upstream issue, produce an artifact, expose a query, or some combination? The contract owner must decide.
10. What provider cost/usage limits and human approvals apply to retries?
11. Which product metrics may be collected without compromising customer/source confidentiality?
12. What exact evidence allows experimental capability promotion and who signs each gate?

## External repository dependencies

| Dependency | Information required before production reliance | Fallback when unavailable/unknown |
| --- | --- | --- |
| `portfolio-tasks` | Authority, task revision, approval/change, classification and lifecycle contract | Reject/hold execution; never infer approval |
| Organization `.github` | Immutable contract distribution, registry, route/result semantics, version/compatibility and trust | Verification-only or disabled; unknown versions fail closed |
| `slugger-generated-demos` or other target | Ownership, base/protection, permitted content, permissions, review/recovery | No publication; retain evidence |
| `consulting-playbook` | Only for future capability: authoritative version, rights, provenance and metadata | Capability remains unavailable; MVP unaffected |

## Resolution governance

Each unknown SHALL receive an owner, decision date, evidence, and impact analysis before the dependent requirement is declared release-ready. Resolutions that change intent update requirements and traceability; architecture answers are recorded downstream without rewriting product need. Silent assumptions by implementation or AI agents are prohibited.
