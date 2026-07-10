# state_machine/

This directory contains the workflow state machine that tracks and transitions Slugger workflow execution state.

## Purpose

The state machine provides a formal, auditable record of where each workflow run is in its lifecycle. It enforces valid state transitions, supports workflow resumption after failure, and enables restartable and retryable execution.

## State Model

Each workflow run moves through defined states, for example:

```
CREATED → RUNNING → [PHASE_COMPLETED → ...] → COMPLETED
                 ↘ FAILED → RETRYING → RUNNING
                 ↘ PAUSED → RUNNING
```

## Conventions

- State transitions are validated; invalid transitions raise exceptions.
- Every transition is recorded with a timestamp and triggering event.
- State is persisted to enable recovery after interruption.
- State definitions are externalized in configuration, not hardcoded.

## Typical Contents

- `state_machine.py` — state machine implementation
- `states.py` — state and transition definitions
- `persistence.py` — state serialization and storage
- `transitions.yaml` — declarative transition rules

## Related

- `orchestrator/` — the orchestrator reads and writes workflow state
- `observability/` — state transitions emit observable events
- `workflow/` — workflow definitions that determine valid state sequences
