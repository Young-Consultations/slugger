# Hello World — Minimal Slugger Pipeline

This example demonstrates the smallest possible end-to-end Slugger run:

1. Load a workflow definition.
2. Execute two agents (`product_vision_agent` → `requirements_agent`).
3. Print the resulting artifacts.

## Requirements

* Slugger installed (`pip install -e .[test]` from the repo root).

## Running

```bash
cd examples/hello_world
python run.py
```

## What it shows

* How to instantiate :class:`WorkflowEngine` with a mock executor.
* How artifacts flow between steps.
* How to read back the workflow result.
