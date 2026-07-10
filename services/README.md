# services/

This directory contains application service implementations that coordinate domain logic across multiple agents, repositories, and external systems.

## Purpose

Services implement higher-level application use cases that span multiple agents or components. They sit between the orchestrator and the domain layer, coordinating interactions without duplicating business logic.

## Conventions

- Services are stateless; state is managed via the state machine or persistence layer.
- Services depend on interfaces, not concrete implementations (dependency injection).
- Each service has a single, well-defined responsibility.
- Services are fully tested via unit and integration tests.

## Typical Contents

- `workflow_service.py` — manages workflow lifecycle (create, execute, resume, archive)
- `artifact_service.py` — manages artifact storage, retrieval, and versioning
- `agent_service.py` — manages agent registration and capability discovery
- `cost_service.py` — tracks and reports AI usage costs

## Related

- `orchestrator/` — the orchestrator calls services to execute workflow logic
- `core/interfaces/` — service interfaces defined in the core layer
- `agents/` — agents invoked by services
- `state_machine/` — state managed and queried by services
