# observability/

This directory contains the observability infrastructure for the Slugger system, including event emission, tracing, and structured logging.

## Purpose

Every important system event must be observable. Observability enables debugging, auditing, cost tracking, performance analysis, and continuous improvement of the AI-SDLC workflow.

## Captured Events

| Category | Examples |
|----------|---------|
| Workflow | Started, phase completed, phase failed, workflow completed |
| Agent | Invoked, prompt sent, response received, artifact produced, retry |
| Provider | Request sent, response received, rate-limited, error |
| Cost | Token usage, estimated cost per invocation |
| Errors | Exceptions, validation failures, timeout |

## Conventions

- Events are emitted as structured objects (not raw strings).
- Every event includes a timestamp, session ID, and event type.
- Observability components are injected via the dependency injection system.
- Observability must not affect business logic correctness.

## Typical Contents

- `event_bus.py` — publish/subscribe event bus
- `event_types.py` — typed event definitions
- `handlers/` — event handlers (logging, metrics, alerting)

## Related

- `logs/` — log files written by observability handlers
- `metrics/` — metrics aggregated from observability events
- `core/events/` — event model definitions
