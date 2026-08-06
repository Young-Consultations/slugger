# Business Rules

Business rules are mandatory product policy. Canonical organization vocabularies remain external; these rules state Slugger decisions without inventing external schemas.

## Authority and governance

| ID | Rule |
| --- | --- |
| BR-01 | A human or externally governed authority MUST approve intent and execution; Slugger, a provider, generated content, a local label, or a successful check cannot grant approval. |
| BR-02 | Approval MUST be attributable, current, scoped to the immutable request/target, and rechecked before consequential mutation. Withdrawal blocks subsequent mutation. |
| BR-03 | Portfolio priority and backlog state are external context; Slugger MUST NOT create, alter, or reinterpret them as execution authority. |
| BR-04 | Only the registered organization control plane may route production cross-repository execution. Slugger SHALL NOT create a second production control plane. |
| BR-05 | Humans retain product/architecture/security judgment, review, merge, release, deployment and production-use decisions. Automation MUST NOT satisfy its own review gate. |

## Intake, validation, and lifecycle

| ID | Rule |
| --- | --- |
| BR-06 | An execution request is one supported capability, target, base and logical delivery with complete versioned context. Missing, contradictory, unsafe, unapproved or unsupported context fails closed. |
| BR-07 | The MVP supported project class is a bounded dependency-minimal Python CLI. Other classes/phases are unsupported until promoted. |
| BR-08 | A provider result is always an untrusted candidate. Provider success, confidence, explanations, or claimed tests are never verification evidence. |
| BR-09 | Candidate output MUST be inventoried and pass applicable path, file, content, structure, syntax, package, dependency, secret and integrity policy before any generated behavior executes. |
| BR-10 | Generated installation, build, tests and smoke behavior occur only in controlled isolation with no publication authority. |
| BR-11 | Publication is allowed only when every required gate is passing, current, correlated to the exact candidate/configuration/input, and integrity-verifiable. Failed, error, timed-out, skipped, unknown, stale, or not-run is not passing. |
| BR-12 | Every status claim MUST distinguish observed fact, provider/user claim, not evaluated, failure, and residual human decision. Narrow verification MUST NOT imply production readiness. |

## Identity, routing, and synchronization

| ID | Rule |
| --- | --- |
| BR-13 | Canonical logical delivery/idempotency identity—not workflow run, attempt, concurrency group, timestamp or randomness—owns deterministic publication identity. |
| BR-14 | Root task, correlation, source and approval provenance MUST survive routing, decomposition, retry, result and publication without silent substitution. |
| BR-15 | At-least-once and concurrent delivery are expected. Concurrency controls MAY reduce overlap but do not prove deduplication. Durable state/ownership classification is required. |
| BR-16 | A completed exact managed delivery is reused. Changed immutable input requires a distinct approved revision/identity according to canonical contract. |
| BR-17 | Upstream context changes do not silently mutate an active/historical run; material changes invalidate affected approval/evidence and require governed reprocessing. |
| BR-18 | Slugger returns canonical results but MUST NOT directly synchronize or invent upstream portfolio lifecycle state. The owning repository/control plane decides synchronization. |

## Publication and approval

| ID | Rule |
| --- | --- |
| BR-19 | Automated output ends at one demonstrably owned open draft PR. Slugger SHALL NOT approve, mark ready, merge, close, release, deploy, force-push unowned work, delete a branch, or silently modify a production repository. |
| BR-20 | A project class, provider, extension, or lifecycle phase is “supported” only after approved user need and scope, named owner, versioned contracts, threats/controls, validation/evidence, failure/recovery, compatibility, documentation, accessibility as applicable, conformance tests, human gate, and product approval are complete. Code presence is insufficient. |
| BR-21 | Ambiguous/unowned/multiply matching/wrong-base/non-draft/closed/merged/conflicting target state is preserved and blocks automation for human reconciliation. Names alone do not prove ownership. |
| BR-22 | Publication contains only verified inventoried files and approved review evidence. Runtime state, credentials, internal prompts where restricted, uncontrolled logs, and provider control data are excluded. |

## Configuration, security, and automation

| ID | Rule |
| --- | --- |
| BR-23 | Safety defaults are deny/fail-closed, draft-only, least privilege, bounded resources, and no optional sensitive telemetry. Configuration cannot disable a mandatory product principle. |
| BR-24 | Secrets are supplied only to the phase that needs them, are not made available to generated behavior, and are never retained or displayed. Suspected disclosure blocks publication and invokes incident policy. |
| BR-25 | Equivalent requests through different supported entry points MUST receive equivalent scope, authority, policy, gate and evidence decisions. |
| BR-26 | Machine and AI actors receive no greater authority than human actors and must use the same canonical contracts, validation, traceability and review boundaries. |
| BR-27 | Retry is bounded, categorized and cost/resource-aware. A retry never bypasses a failed policy/security gate and reruns all evidence invalidated by changed inputs, output, environment or configuration. |

## Evidence, retention, and exceptions

| ID | Rule |
| --- | --- |
| BR-28 | Required run evidence includes identities, input/scope, versions, provider provenance, manifest, checks, state history, errors, publication and outstanding decisions, protected against undetected change. |
| BR-29 | Retention, access, export and deletion follow approved classification policy. Cleanup requires proven ownership and is itself auditable. |
| BR-30 | Any policy exception requires an accountable human, rationale, scope, risk, approval and expiry. No exception may authorize self-approval, automatic merge, secret exposure, uncontained generated execution, false evidence, or ambiguous ownership. |
| BR-31 | A canonical contract major version or required semantic unknown to Slugger is rejected; compatibility is never guessed. |
| BR-32 | Experimental capabilities are visibly labeled, isolated from supported execution, and cannot produce evidence or status that could be mistaken for supported product results. |

## Validation summary

Every P0 acceptance suite SHALL include rule-level positive and negative cases. Rules BR-01, BR-08–11, BR-13, BR-19, BR-21, BR-24, BR-30 and BR-31 are non-waivable release safety invariants.
