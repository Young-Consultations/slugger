# models/

This directory contains domain model definitions, data transfer objects, and value objects for the Slugger system.

## Purpose

Centralizing model definitions ensures consistency across agents, workflows, and providers. Models describe the shape of data as it flows through the system.

## Conventions

- Models are implemented as Python dataclasses or Pydantic models.
- All fields are fully type-annotated.
- Models are immutable where practical.
- Models do not contain business logic; they are pure data containers.
- Serialization and validation are handled by the model layer.

## Typical Contents

- `agent.py` — agent metadata and capability models
- `artifact.py` — artifact envelope with traceability metadata
- `workflow.py` — workflow definition and execution state models
- `provider.py` — AI provider configuration models
- `prompt.py` — prompt template and invocation models
- `event.py` — observability event models

## Related

- `core/` — interfaces and abstract base classes that use these models
- `agents/` — agents that produce and consume model instances
- `validators/` — validators that operate on model instances
