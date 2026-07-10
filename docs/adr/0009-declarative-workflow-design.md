# ADR 0009: Declarative Workflow Design

Status: Accepted

## Context

Slugger orchestrates multi-step SDLC workflows that span many agents, artifacts, quality gates, and approval steps. Encoding these workflows purely in Python would create several problems:
- Workflows become tightly coupled to implementation details.
- Non-engineers cannot read or modify workflow definitions.
- Workflows cannot be versioned, replayed, or inspected without executing code.
- Restartability and observability are difficult to retrofit into imperative code.

A declarative approach separates workflow intent from execution mechanics.

## Decision

Adopt **declarative YAML-based workflow definitions** as the primary format for describing Slugger workflows.

Key design decisions:
1. Workflow definitions live in the `workflow/` directory as `.yaml` files.
2. Each workflow file declares: `name`, `version`, `description`, `inputs`, `outputs`, `steps`, `quality_gates`, and `recovery_behavior`.
3. Individual steps reference agents by capability name rather than class name.
4. Quality gates are defined as conditions that must pass before a step advances.
5. The workflow engine (`workflow/`) interprets these definitions at runtime.
6. Workflows are **observable** (each step emits events), **restartable** (execution state is persisted), **retryable** (configurable retry policies per step), and **composable** (workflows can call sub-workflows).
7. Custom logic that cannot be expressed declaratively is implemented as agent plugins, not embedded in workflow YAML.

## Consequences

**Positive:**
- Workflows are human-readable and editable by product managers and architects.
- Workflow definitions are version-controlled alongside code.
- Execution state persistence enables restart without rerunning completed steps.
- Workflow behavior can be validated without executing agents.
- New workflow patterns can be composed without writing code.
- Observability is a first-class concern built into the engine.

**Negative:**
- YAML has limited expressiveness; complex branching logic may require extension mechanisms.
- Schema validation for workflow YAML must be maintained alongside the engine.
- Debugging declarative workflows is more indirect than stepping through imperative code.
- The workflow engine adds architectural complexity.
