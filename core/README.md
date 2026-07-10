# core/

This directory contains the foundational abstractions, interfaces, and shared utilities for the Slugger system.

## Purpose

The `core/` layer defines the contracts (interfaces and abstract base classes) that all agents, providers, plugins, and workflows depend on. It contains no concrete implementations of external dependencies.

## Conventions

- Depend only on the Python standard library and project-defined interfaces.
- Never import from `agents/`, `providers/`, or `plugins/` — those layers depend on `core/`, not the reverse.
- All public interfaces must be fully type-annotated.
- Each module is documented with a docstring describing its responsibility.

## Typical Contents

- `interfaces/` — abstract base classes for agents, providers, workflows, and validators
- `models/` — domain model data classes and value objects
- `exceptions/` — project-wide exception hierarchy
- `events/` — event definitions for the observability system
- `utils/` — stateless utility functions with no external dependencies

## Related

- `agents/` — implements agent interfaces defined here
- `providers/` — implements provider interfaces defined here
- `plugins/` — extends interfaces defined here
- `validators/` — implements validator interfaces defined here
