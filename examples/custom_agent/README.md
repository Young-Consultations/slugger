# Custom Agent Example

Demonstrates how to implement a custom Slugger agent and integrate it into a workflow.

## Steps

1. Subclass :class:`agents.base.BaseAgent`.
2. Declare metadata and capabilities.
3. Implement :meth:`_execute` to produce artifacts.
4. Register the agent with :class:`agents.registry.AgentRegistry`.
5. Run a workflow that references the agent's name.

## Running

```bash
cd examples/custom_agent
python run.py
```

## Key concepts

* `AgentMetadata.name` must match the `agent` field in the YAML workflow recipe.
* `_execute` returns a list of :class:`models.artifact.Artifact` objects.
* Use :meth:`BaseAgent.create_artifact` to build artefacts with correct provenance.
