# Observability Architecture

> Next-MVP audit correlation spans request, proof decision, reconciliation, Codex (implement only), validation, draft create/reuse, result validation, and result delivery attempts. Telemetry is sanitized and may not substitute for canonical results/evidence or grant authorization.

## Principles

Mandatory run evidence/audit proves lifecycle facts; observability diagnoses system operation. Logs, metrics and traces are sanitized derivative signals and never substitute for gates. All signals correlate by delivery, run, attempt, phase and operation IDs where classification permits. Provider prompts, candidate content, secrets and raw generated output are excluded by default.

## Structured logging

Emit schema-versioned events with timestamp, severity, component, environment/release, event name, correlation identities, phase/state, outcome/error category, duration and safe diagnostic reference. Use allowlisted structured fields—never string concatenation of untrusted content. Central redaction is defense in depth after source minimization. Audit access and redaction events; bound volume and retain according to classification.

## Metrics

| Category | Examples |
|---|---|
| Demand | Accepted/rejected deliveries, active runs, queue depth/age, capability/mode counts |
| Outcome | Terminal categories, gate pass/non-pass by type, handoff/reuse/block counts |
| Latency | Intake, provider, inventory, verification, evidence, publication and end-to-end histograms |
| Reliability | Retry/resume/reconciliation, lease conflict, stale evidence, ambiguous target, external error rate |
| Security | Authority denial, unsafe artifact/dependency, secret detection, sandbox limit/egress denial, contract rejection |
| Resources/cost | Tokens/cost where permitted, CPU/memory/storage, candidate size/files, workspace cleanup backlog |
| Integration | Availability/rate limit/circuit state by dependency, result-delivery backlog |

Metric labels must be bounded and contain no user content, raw IDs where privacy disallows them, paths, tokens, or high-cardinality error text.

## Distributed tracing

Trace inbound request through coordinator and each adapter using correlation/causation. Create spans for authority verification, provider operation, inventory, each gate, evidence sealing and target reconciliation. Record only digest/reference and categorized outcome. Propagate trace context only to trusted integrations under policy; never allow external trace data to override canonical identity.

## Health monitoring

* **Liveness:** process can make internal progress; never depends on all external systems.
* **Readiness:** can safely accept the declared mode/capability, including store/migration/config/credential prerequisites.
* **Dependency health:** independently reports degraded provider, authority, sandbox, evidence and target adapters.
* **Business safety health:** detects stuck leases, backlog age, cleanup failures, reconciliation/manual-review queue, evidence integrity and result outbox lag.

Readiness failure prevents new acceptance or returns explicit unavailable state; it never bypasses a gate. Existing queries/evidence should remain available when safe.

## Diagnostics and alerting

Human run summary shows what happened, verified versus claimed facts, failed phase/category, retryability, retained workspace/evidence policy, target occurrence, and next action. Alerts cover security events, inability to write audit/evidence, repeated contract rejection, stale/ambiguous publication, SLO burn, resource exhaustion and cleanup retention breach. Each alert has owner, severity, runbook, dedupe and escalation; no automated response may merge/delete/force target work.

## SLO governance

Requirements require baselining before final targets. Measure intake acceptance, time-to-reviewed-draft, terminal-result completeness, zero publication-after-failed-gate, deduplication correctness and evidence availability. Product/operations must approve numeric SLOs and error budgets; security/correctness invariants are not traded for latency.
