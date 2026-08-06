# Nonfunctional Requirements

Measurements apply to the supported MVP reference workload: one bounded dependency-minimal Python CLI project within documented input/file/resource limits and a healthy supported environment. External provider, dependency-source, and GitHub latency SHALL be measured separately from Slugger-controlled overhead. Threshold changes require product approval and traceability.

## Performance and scalability

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-PER-01 | Intake, contract/policy validation, and run creation SHALL complete within 5 seconds at p95, excluding unavailable external authority queries. | 100-run reference test; report internal and external time separately. | P1 | VG-01 |
| NFR-PER-02 | Slugger-controlled overhead excluding provider, dependency transfer, installation, tests, smoke, and GitHub calls SHALL be ≤30 seconds at p95 for ≤500 files/50 MiB. | Timed reference workload. | P1 | VG-01 |
| NFR-PER-03 | Every external call and generated process MUST have configurable deadlines; default end-to-end attempt deadline SHALL be documented and a timeout SHALL terminate safely within 30 seconds of expiry. | Fault test for each boundary. | P0 | VG-04, VG-05 |
| NFR-PER-04 | Output capture MUST be bounded per process and per run; truncation SHALL preserve the beginning/end, byte counts, and explicit truncation marker. | Oversized-output test; no memory exhaustion. | P0 | VG-04 |
| NFR-SCL-01 | Run, workspace, evidence, and publication identity MUST be isolated so at least 10 concurrent reference runs can execute without state crossover or correctness degradation. | Concurrency test; zero cross-run artifacts/credentials/status. | P1 | VG-04, VG-05 |
| NFR-SCL-02 | Capacity limits (concurrency, files, bytes, duration, retained runs) SHALL be configurable, observable, and enforced before overload; refusal SHALL not corrupt active runs. | Boundary/load tests. | P1 | VG-05 |

## Security and privacy

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-SEC-01 | All actors, calls, providers, and target operations MUST use least privilege; generation and verification MUST receive no publication credential. | Credential-presence tests at every phase; zero unauthorized credentials. | P0 | VG-03, VG-04 |
| NFR-SEC-02 | Generated files, builds, dependencies, tests, and commands MUST be treated as untrusted and contained from Slugger source/state, other runs, host secrets, and protected networks/resources. | Threat-model conformance plus traversal, symlink, process, filesystem, environment, and egress adversarial tests. | P0 | VG-04 |
| NFR-SEC-03 | Secret values and credentials MUST NOT be written to prompts, artifacts, manifests, logs, telemetry, PR content, process arguments visible to generated code, or retained environments. | Seeded-secret scanning of all outputs yields zero disclosure. | P0 | VG-02, VG-04 |
| NFR-SEC-04 | Dependency acquisition MUST use explicitly approved sources and integrity controls and SHALL support deny-by-default network policy. | Unapproved source/tamper/offline tests fail closed. | P0 | VG-04 |
| NFR-SEC-05 | Inputs and outputs MUST be checked for injection, unsafe paths, ambiguous normalization, malicious links/special files, oversized content, prohibited executable behavior, and embedded secrets before trust escalation. | Published adversarial corpus achieves 100% block rate for defined prohibited cases. | P0 | VG-04 |
| NFR-SEC-06 | Security-relevant dependencies and release artifacts SHALL be scanned to the approved organizational policy; unresolved critical findings MUST block release unless an accountable human records an approved, expiring exception. | Release evidence shows scan and disposition. | P1 | VG-03 |
| NFR-SEC-07 | Data SHALL be encrypted in transit across external boundaries; sensitive retained evidence SHALL use approved access controls and encryption at rest where supported by the operating environment. | Configuration/security review and access tests. | P1 | VG-02 |
| NFR-SEC-08 | A documented threat model covering trust boundaries, abuse cases, provider compromise, supply chain, publication, and recovery SHALL be reviewed for every supported capability and at least annually. | No release with missing/currently unreviewed threat model. | P1 | VG-04, VG-06 |

## Reliability, availability, and recovery

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-REL-01 | All required gates and ambiguous states MUST fail closed; no single exception, timeout, malformed response, or unavailable dependency may produce a passing aggregate or publication. | Fault injection at every boundary; zero false success/publication. | P0 | VG-04, VG-05 |
| NFR-REL-02 | Stable-delivery handling MUST be idempotent under at-least-once, reordered, and concurrent duplicate delivery. | 100 sequential and 20 concurrent duplicate scenarios: at most one managed open draft and no overwrite of unowned work. | P0 | VG-05 |
| NFR-REL-03 | State updates and evidence references MUST be durable at phase boundaries and recover consistently after abrupt termination. | Kill/restart at every boundary; no completed phase silently lost or partial phase passed. | P0 | VG-02, VG-05 |
| NFR-REL-04 | Integrity protection SHALL detect candidate, manifest, evidence, or immutable-input change before reuse/publication. | One-bit and structural tampering tests detected 100%. | P0 | VG-02 |
| NFR-REL-05 | For Slugger-controlled defects in a supported environment, ≥99% of accepted reference runs SHALL reach a truthful terminal state; provider/user/external failures are categorized separately. | Rolling release qualification sample ≥200 or all runs if fewer. | P1 | VG-05 |
| NFR-AVL-01 | No always-on Slugger service is required for CLI/job execution. When deployed as an on-demand service, a separate approved SLO SHALL define availability; absent that deployment, availability is reported as job-start success and not uptime. | Deployment profile documents applicable measure. | P1 | VG-06 |
| NFR-REC-01 | Recovery point objective SHALL be the last committed phase boundary; state/evidence backup restoration for supported persistent deployments SHALL meet RPO ≤5 minutes and RTO ≤4 hours, or disclose a stricter deployment profile. | Quarterly restore exercise. | P1 | VG-05 |
| NFR-REC-02 | Recovery procedures MUST preserve ambiguous/unowned target state and SHALL never automatically delete branches, close PRs, or rewrite user work to recover. | Unsafe-state recovery suite. | P0 | VG-03, VG-05 |

## Observability, auditability, and telemetry

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-OBS-01 | Every event/log/evidence item SHALL carry run ID, delivery ID, correlation ID, phase, severity/category, timestamp in UTC, and component identity when those exist. | Schema conformance ≥99.9%; missing mandatory correlation fails evidence finalization. | P0 | VG-02 |
| NFR-OBS-02 | Logs SHALL be structured, ordered or sequenceable, bounded, safely redacted, and distinguish user error, policy refusal, provider/external error, timeout, internal defect, and security event. | Golden/fault tests; seeded secrets absent. | P0 | VG-02, VG-05 |
| NFR-OBS-03 | Audit records for authority, policy decisions, state transitions, evidence integrity, retries, and target mutation SHALL be append-only/tamper-evident within the supported retention boundary. | Mutation detection and access test. | P0 | VG-02, VG-03 |
| NFR-OBS-04 | Metrics SHALL include accepted/rejected/terminal runs, phase duration/outcome, publication/reuse/block decisions, retry counts, resource consumption, provider usage where available, and redaction/security events without sensitive payloads. | Metric catalog and synthetic-run validation. | P1 | VG-02 |
| NFR-OBS-05 | Telemetry collection SHALL be documented, minimal, configurable, and disabled from exporting sensitive content by default; disabling optional telemetry MUST NOT disable local evidence. | Offline and opt-out tests. | P1 | VG-02 |
| NFR-OBS-06 | A user SHALL be able to obtain current/terminal status and evidence location for a known authorized run within 2 seconds p95 from local durable state. | 1,000-run state query benchmark. | P1 | VG-05 |

## Maintainability, extensibility, and interoperability

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-MNT-01 | Supported MVP behavior SHALL remain separable from experimental full-SDLC capabilities; experimental absence/failure MUST NOT affect MVP startup or execution. | Architecture/conformance tests and minimal installation exercise. | P0 | VG-06 |
| NFR-MNT-02 | Requirement, contract, policy, prompt, catalog, and evidence versions SHALL be explicit; changes SHALL document compatibility, migration, deprecation, and traceability. | Release review finds no unversioned behavioral change. | P1 | VG-02, VG-06 |
| NFR-MNT-03 | Product policy SHALL be defined once per authoritative scope and evaluated consistently across supported entry points. | Cross-entry conformance scenarios yield same decision. | P1 | VG-05 |
| NFR-EXT-01 | A new project class or lifecycle capability SHALL be addable without weakening existing gates and only after meeting BR-20 promotion criteria. | Existing suite unchanged/pass plus new conformance pack. | P2 | VG-06 |
| NFR-INT-01 | External contracts SHALL be provider/repository neutral where organization ownership permits and use version negotiation or explicit rejection; unknown major versions MUST fail closed. | Contract compatibility suite for current, supported previous, and unknown versions. | P0 | VG-06, VG-07 |
| NFR-INT-02 | Machine-readable artifacts SHALL declare format identity/version, stable identifiers, timestamps, integrity information, and explicit absent/not-applicable semantics. | Schema and round-trip validation. | P0 | VG-02 |
| NFR-PORT-01 | The supported CLI/job product SHALL run on documented supported operating environments with Python 3.11+; environment-specific containment limitations MUST be disclosed and cannot silently reduce required security. | Release matrix on each supported environment. | P1 | VG-06 |
| NFR-DEP-01 | Slugger SHALL be independently installable, configured, upgraded, rolled back, and executed without installing or executing experimental subsystems or cloning external repositories except when an explicitly invoked interface requires versioned contract material. | Clean-environment install/run test. | P0 | VG-06, VG-07 |

## Configuration and deployment independence

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-CFG-01 | Environment-dependent values, limits, endpoints, policies, retention, and provider selection SHALL be externally configurable, validated before use, and represented in effective configuration evidence without secrets. | Invalid/missing/boundary tests; effective config digest recorded. | P0 | VG-02, VG-06 |
| NFR-CFG-02 | Precedence and defaults SHALL be documented and deterministic; safety-critical defaults MUST be deny/fail-closed, draft-only, least privilege, and no optional external telemetry. | Configuration matrix test. | P0 | VG-03, VG-04 |
| NFR-CFG-03 | Configuration changes that affect evidence validity SHALL invalidate/re-run dependent gates rather than silently altering an active run. | Mid-run change tests. | P0 | VG-02, VG-05 |
| NFR-DEP-02 | Slugger SHALL not require access to `portfolio-tasks`, the organization repository, consulting playbook, or publication target source trees at build time; runtime interactions occur only through their approved contracts. | Isolated build/test without external checkouts. | P0 | VG-07 |

## Usability and accessibility

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-USA-01 | Human-facing status SHALL use plain language and present intent/scope, progress, verified facts, claims, failures, residual risks, evidence links, and next human action distinctly. | ≥80% of representative primary users correctly identify outcome, failed gate, and next action in usability study (n≥8/persona mix). | P1 | VG-02, VG-03 |
| NFR-USA-02 | Destructive or consequential actions SHALL require explicit intent; automation SHALL not rely on color, icon, or position alone to communicate status. | UX review and keyboard/text-only scenarios. | P1 | VG-03 |
| NFR-ACC-01 | Any web UI introduced SHALL meet WCAG 2.2 AA. CLI and text artifacts SHALL support keyboard-only use, semantic headings/tables, non-color status labels, and machine-readable equivalents. | Automated checks plus manual keyboard/screen-reader review for web; text audit for CLI/docs. | P1 | VG-03 |
| NFR-ACC-02 | Diagnostic messages SHOULD identify the field/phase, reason, impact, and remediation without requiring access to confidential raw logs. | Golden-message review covers all failure categories. | P1 | VG-05 |

## Compliance, documentation, testability, automation, and AI compatibility

| ID | Requirement | Measure / acceptance | Priority | Vision |
| --- | --- | --- | --- | --- |
| NFR-CMP-01 | Slugger SHALL preserve records needed for authorization, provenance, review, and target mutation under an approved retention/access policy and support lawful deletion/export where applicable. | Retention, access, export, deletion tests; OQ-10 resolves jurisdictional details. | P1 | VG-02, VG-03 |
| NFR-CMP-02 | Data classification, retention duration, evidence ownership, license obligations, and personal/confidential-data handling MUST be approved before production use with such data. | Release governance checklist; unresolved classification blocks affected use. | P0 | VG-03 |
| NFR-DOC-01 | Each supported capability SHALL document purpose, users, inputs, outputs, limits, prerequisites, security boundary, errors, recovery, evidence, and human responsibilities. | Release documentation checklist 100% complete. | P0 | All |
| NFR-DOC-02 | Documentation SHALL label supported, deprecated, experimental, and future behavior consistently and SHALL NOT claim production readiness from narrow verification. | Release terminology audit has zero conflicting claims. | P0 | VG-03, VG-06 |
| NFR-TST-01 | Every P0/P1 requirement and business rule SHALL trace to at least one automated conformance test or an explicitly justified human verification; every P0 negative/fail-closed path MUST be automated. | Traceability report has 100% coverage and no unexplained gap. | P0 | VG-02 |
| NFR-TST-02 | Test environments SHALL control time, identity, inputs, external simulations, and random sources so policy/idempotency outcomes are reproducible. | Three repeated runs produce identical normalized verdicts. | P1 | VG-05 |
| NFR-AUT-01 | All supported operations SHALL offer stable non-interactive input, machine-readable status/result/evidence, deterministic exit categories, and no hidden prompt in automation mode. | End-to-end headless acceptance suite. | P0 | VG-01, VG-06 |
| NFR-AUT-02 | Contracts and evidence SHALL be schema-validatable, additive-change tolerant within a compatible version, and suitable for future automated traceability and policy evaluation. | Consumer-driven contract and unknown-field tests. | P1 | VG-02, VG-06 |
| NFR-AI-01 | AI-originated content SHALL carry provenance and remain untrusted until independently validated; a model's confidence or completion claim MUST NOT satisfy a gate. | Inject false provider claims; aggregate remains based only on observed evidence. | P0 | VG-02, VG-03 |
| NFR-AI-02 | AI requests SHALL include bounded objective, allowed context/actions, output expectations, and governing constraints; response handling SHALL tolerate nondeterminism while preserving deterministic policy decisions. | Prompt-contract and varied-response conformance tests. | P0 | VG-04, VG-06 |
| NFR-AI-03 | Provider/model identity, applicable version, request digest, session/correlation reference, usage/cost where available, and result classification SHALL be recorded without exposing protected reasoning or secrets. | Evidence schema validation across provider success/failure. | P1 | VG-02, VG-06 |
