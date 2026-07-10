# Testing Strategy

## Unit Tests
Validate models, validators, registries, memory backends, and workflow behavior with mock dependencies.

## Contract Tests
Ensure providers, plugins, and services honor their interfaces consistently across implementations.

## Recipe Validation
Workflow YAML files are parsed and validated as configuration assets before runtime.

## Design Principles
- Prefer deterministic tests over network-dependent tests.
- Use mock providers and mock GitHub services for isolation.
- Cover both success and failure paths for orchestration components.
