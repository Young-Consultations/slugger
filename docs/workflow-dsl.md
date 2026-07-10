# Workflow DSL Specification

Slugger workflows are declarative YAML documents that describe repeatable AI-SDLC processes. The DSL is designed to be explicit, traceable, and safe to validate before execution.

## Top-Level Schema

```yaml
name: full-sdlc
version: 1.0.0
description: Complete AI-SDLC workflow
tags: [sdlc, default]
metadata:
  owner: platform
defaults:
  retry_policy:
    max_attempts: 2
    backoff_seconds: 1
steps: []
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Stable workflow identifier. |
| `version` | string | yes | Semantic version of the recipe. |
| `description` | string | no | Human-readable purpose. |
| `tags` | list[string] | no | Discovery metadata. |
| `metadata` | map | no | Arbitrary extension data. |
| `defaults` | map | no | Shared retry or quality gate defaults. |
| `steps` | list[step] | yes | Ordered list of executable workflow steps. |

## Step Definition

```yaml
steps:
  - name: requirements
    agent: requirements_agent
    description: Convert vision into structured requirements
    inputs: [product_vision]
    outputs: [requirements]
    retry_policy:
      max_attempts: 2
      backoff_seconds: 2
    quality_gates:
      - validator: artifact_validator
        config:
          require_content: true
    on_failure: stop
    recovery:
      action: emit_artifact
      artifact_name: requirements_failure_report
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Unique step name within the workflow. |
| `agent` | string | yes | Registered agent name. |
| `description` | string | no | Step intent. |
| `inputs` | list[string] | no | Artifact names required before execution. |
| `outputs` | list[string] | no | Expected artifact names after execution. |
| `retry_policy` | map | no | Retry behavior for transient failures. |
| `quality_gates` | list[gate] | no | Validation rules applied after execution. |
| `on_failure` | string | no | `stop`, `continue`, or `recover`. |
| `recovery` | map | no | Recovery instructions. |
| `metadata` | map | no | Additional runtime hints. |

## Quality Gates

```yaml
quality_gates:
  - name: outputs-present
    validator: artifact_validator
    required: true
    config:
      require_content: true
```

## Retry Policy

```yaml
retry_policy:
  max_attempts: 3
  backoff_seconds: 5
  retry_on:
    - ProviderError
```

## Recovery Behavior

Supported recovery actions in the initial foundation:
- `emit_artifact`
- `substitute_agent`
- `skip`

## Annotated Example: Full SDLC Workflow

```yaml
name: full-sdlc
version: 1.0.0
steps:
  - name: vision
    agent: product_vision_agent
    outputs: [product_vision]
  - name: requirements
    agent: requirements_agent
    inputs: [product_vision]
    outputs: [requirements]
  - name: architecture
    agent: system_design_agent
    inputs: [requirements]
    outputs: [system_design]
  - name: implementation
    agent: code_generator_agent
    inputs: [requirements, system_design]
    outputs: [generated_code]
```

## Annotated Example: Code Review Workflow

```yaml
name: code-review
version: 1.0.0
steps:
  - name: review
    agent: code_review_agent
    inputs: [generated_code]
    outputs: [code_review]
  - name: security
    agent: security_review_agent
    inputs: [generated_code]
    outputs: [security_review]
```

## Authoring Rules

- Prefer stable artifact names over implicit positional dependencies.
- Keep steps capability-focused and single-purpose.
- Declare all required outputs so validation can enforce traceability.
- Store workflow recipes in `workflow/recipes/` and validate them before execution.
