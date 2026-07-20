# Workflow Customization Example

This sample demonstrates how to keep a workflow recipe beside an example and validate it with Slugger's workflow parser.

## Running

```bash
cd examples/workflow_customization
python run.py
```

## What it shows

* Defining a custom workflow in YAML.
* Parsing and validating the workflow with `WorkflowParser` and `WorkflowValidator`.
* Inspecting step order, agent bindings, and declared outputs before wiring the recipe into a runtime.
