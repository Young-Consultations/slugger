# examples/

This directory contains runnable examples demonstrating how to use the Slugger system.

## Purpose

Examples lower the barrier to adoption by showing how to invoke agents, define workflows, configure providers, and extend the system with plugins.

## Conventions

- Each example is self-contained in its own subdirectory.
- Each example includes a `README.md` explaining what it demonstrates and how to run it.
- Examples use only public interfaces and documented configuration.
- Examples are kept up to date as APIs evolve.

## Typical Contents

- `hello_world/` — minimal end-to-end run of the Slugger pipeline
- `custom_agent/` — how to implement and register a custom agent
- `custom_provider/` — how to configure an alternative AI provider
- `workflow_customization/` — how to define a custom workflow in YAML

## Running examples

Each runnable example provides a `run.py` entrypoint and can be launched from its directory:

```bash
cd examples/hello_world && python run.py
cd ../custom_agent && python run.py
cd ../custom_provider && python run.py
cd ../workflow_customization && python run.py
```

All samples use deterministic local implementations so they can run without API keys.

## Related

- `docs/` — architecture and interface documentation referenced by examples
- `agents/` — agent implementations shown in examples
- `workflow/` — workflow definitions used in examples
