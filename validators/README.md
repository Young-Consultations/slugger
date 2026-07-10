# validators/

This directory contains artifact and output validators for the Slugger system.

## Purpose

Validators enforce quality gates by checking that artifacts, agent outputs, and workflow states satisfy defined criteria before a workflow phase advances. They provide the quality assurance layer of the AI-SDLC pipeline.

## Conventions

- Every validator implements the `Validator` interface defined in `core/interfaces/`.
- Validators return structured results with a pass/fail status and descriptive messages.
- Validators are composable: multiple validators can be chained for a single artifact type.
- Validators do not modify artifacts; they only inspect and report.

## Typical Contents

- `requirements_validator.py` — validates completeness and consistency of requirements
- `architecture_validator.py` — validates architectural decisions against defined principles
- `code_validator.py` — validates generated code against coding standards
- `test_coverage_validator.py` — validates test coverage thresholds
- `artifact_schema_validator.py` — validates artifact structure against JSON Schema

## Related

- `core/interfaces/` — the `Validator` abstract interface
- `orchestrator/quality_gate.py` — quality gate that invokes validators
- `workflow/` — workflow definitions that specify which validators apply to each phase
