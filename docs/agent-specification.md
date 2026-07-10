# Agent Specification

Slugger agents are modular runtime components that perform a single responsibility within the AI-SDLC. They are designed to be composable, observable, and replaceable.

## Agent Contract

Every agent must expose:
- **Metadata**: stable identity, version, description, category, inputs, outputs, tags.
- **Capabilities**: explicit declarations of what the agent can do.
- **Lifecycle**: initialize, validate inputs, execute, validate outputs, emit telemetry, finalize.
- **Inputs**: execution context plus referenced artifacts.
- **Outputs**: one or more artifacts with full provenance metadata.

## Lifecycle

1. Resolution
2. Input validation
3. Execution
4. Output validation
5. Observation
6. Completion

## Agent Categories

- Planning Agents
- Architecture Agents
- Development Agents
- QA Agents
- Operations Agents
- Support Agents

## Metadata Schema

```yaml
name: requirements_agent
version: 1.0.0
description: Produce a requirements document from a product vision artifact
category: planning
inputs: [product_vision]
outputs: [requirements]
tags: [analysis, specification]
provider: mock
```

## Capability Model

Capabilities are explicit contracts rather than informal labels. A capability declaration should answer what the agent does, what artifact types it reads, what artifact types it produces, and which quality expectations apply.

## Artifact-Based Communication

Agents do not call each other directly. They collaborate by reading and writing artifacts stored in a shared artifact store. This pattern provides deterministic handoffs, auditability, easier retries, validation at boundaries, and plugin-safe extension points.

## Quality Gate Integration

Agents are workflow-aware but not workflow-coupled. Common gate checks include artifact presence, non-empty content, schema validity, capability compatibility, and policy compliance.

## Implementation Expectations

- Use typed dataclasses for metadata and execution inputs.
- Prefer composition and injected dependencies over inheritance-heavy designs.
- Keep provider calls behind abstractions.
- Emit structured execution events for start, success, and failure.
- Avoid hidden state; persist meaningful outputs as artifacts or memory entries.
