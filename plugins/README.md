# plugins/

This directory contains dynamically discoverable plugins that extend the Slugger system.

## Purpose

The plugin architecture allows new agents, providers, validators, workflow steps, and artifact generators to be added without modifying core system code. Plugins are discovered and registered at runtime.

## Plugin Types

| Type | Description |
|------|-------------|
| `agents/` | Additional AI agent implementations |
| `providers/` | Alternative AI model providers |
| `validators/` | Custom artifact and output validators |
| `workflow_steps/` | Custom workflow step implementations |
| `artifact_generators/` | Custom artifact format generators |

## Conventions

- Each plugin is a self-contained Python package.
- Plugins declare their type and metadata in a `plugin.yaml` manifest.
- Plugins are discovered by scanning this directory at startup.
- Plugins must implement the relevant interface from `core/interfaces/`.
- Plugin names are globally unique within their type category.

## Plugin Manifest (`plugin.yaml`)

```yaml
name: my_plugin
type: agent
version: 1.0.0
description: "Short description of the plugin."
capabilities:
  - capability_name
dependencies: []
```

## Related

- `core/` — interfaces that plugins must implement
- `orchestrator/` — the orchestrator that discovers and invokes plugins
- `agents/`, `providers/` — built-in implementations following the same contracts
