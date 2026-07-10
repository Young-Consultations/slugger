# orchestrator/

This directory contains the Master Orchestrator that coordinates the entire Slugger AI-SDLC workflow.

## Purpose

The orchestrator is the central controller that sequences agent invocations, manages workflow state, enforces quality gates, handles errors and retries, and produces the final set of SDLC artifacts.

## Responsibilities

- Load and validate workflow definitions from `workflow/`
- Resolve and invoke agents in the correct order
- Pass artifacts between agents
- Monitor workflow state via `state_machine/`
- Emit observability events via `observability/`
- Enforce quality gates before advancing workflow phases
- Support workflow restart and recovery

## Design Principles

- The orchestrator is workflow-definition-driven; behavior changes by editing YAML, not code.
- Agents are resolved dynamically through the plugin registry.
- The orchestrator does not contain agent-specific logic.
- All orchestrator actions are observable and auditable.

## Typical Contents

- `orchestrator.py` — main orchestrator entry point
- `phase_runner.py` — executes a single workflow phase
- `quality_gate.py` — evaluates phase quality criteria
- `agent_resolver.py` — resolves agent implementations from the registry

## Related

- `agents/` — agents invoked by the orchestrator
- `workflow/` — YAML workflow definitions consumed by the orchestrator
- `state_machine/` — workflow state tracked and updated by the orchestrator
- `plugins/` — dynamically discovered agents and extensions
