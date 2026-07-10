# workflow/

This directory contains declarative workflow definitions that drive the Slugger AI-SDLC pipeline.

## Purpose

Workflows describe the sequence of phases, agent invocations, artifact handoffs, quality gates, and recovery behavior for each type of software project the system can produce. Changing behavior is done by editing workflows, not code.

## Conventions

- Workflows are defined in YAML.
- Each workflow file describes a complete end-to-end SDLC workflow or a reusable sub-workflow.
- Workflow files are named after their purpose (e.g., `standard_sdlc.yaml`).
- Workflows reference agents by name; agents are resolved at runtime by the orchestrator.
- Quality gates are declared inline within each phase definition.

## Workflow File Structure

```yaml
name: standard_sdlc
version: 1.0.0
description: "Standard AI-SDLC workflow for a new software project."
phases:
  - name: requirements
    agent: requirements_agent
    inputs: [product_brief]
    outputs: [requirements_doc]
    quality_gate:
      validator: requirements_validator
```

## Typical Contents

- `standard_sdlc.yaml` — default end-to-end workflow
- `rapid_prototype.yaml` — abbreviated workflow for rapid prototyping
- `documentation_only.yaml` — workflow that produces only documentation artifacts

## Related

- `orchestrator/` — the orchestrator loads and executes these definitions
- `agents/` — agents referenced by workflow phases
- `validators/` — validators referenced by quality gate definitions
