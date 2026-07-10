# ADR 0011: Observability and Telemetry Architecture

Status: Accepted

## Context

Slugger orchestrates complex multi-agent workflows that consume AI tokens, interact with external providers, generate artifacts, and execute long-running processes. Without structured observability, diagnosing failures, optimizing cost, and understanding system behavior are impractical.

Requirements for observability:
- Track execution time, retries, and outcomes per agent and workflow step.
- Record AI token usage and estimated cost per workflow run.
- Capture warnings, errors, and agent decisions with sufficient context for post-mortem analysis.
- Support workflow state inspection without halting execution.
- Expose metrics that can drive continuous improvement.

## Decision

Adopt a **structured observability architecture** built into the Slugger core, implemented in `observability/`.

Key decisions:
1. **Structured logging** — all log entries are structured (JSON or equivalent) with fields: `timestamp`, `level`, `agent`, `workflow`, `step`, `event_type`, `message`, and optional `metadata`.
2. **Execution events** — each significant action emits a typed event: `WorkflowStarted`, `StepStarted`, `StepCompleted`, `StepFailed`, `AgentInvoked`, `ArtifactCreated`, `TokenUsageRecorded`, `QualityGatePassed`, `QualityGateFailed`.
3. **Metrics collection** — counters and timers are captured for: execution time, token usage, estimated AI cost, retry count, artifact count, and workflow completion rate.
4. **Workflow state persistence** — execution state is written to `state_machine/` after each step to support restart and audit.
5. **Log destination** — logs are written to `logs/` by default; production deployments may stream to external sinks (e.g., CloudWatch, Datadog) via configurable handlers.
6. **Observability is not optional** — every agent and workflow step must emit events; it is a required part of the agent contract.

## Consequences

**Positive:**
- Failures can be diagnosed from structured logs without code instrumentation.
- AI cost is transparent and can be optimized.
- Workflow state can be inspected and resumed after interruption.
- Continuous improvement is data-driven (metrics inform prompt and workflow optimization).
- Compliance and audit requirements can be met through event logs.

**Negative:**
- Structured logging adds a small performance overhead.
- Log volume can become large for complex workflows; log rotation and retention policies are required.
- Maintaining consistency of event schemas across agents requires discipline and schema validation.
