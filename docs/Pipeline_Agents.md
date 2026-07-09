# Pipeline Agents: Requirements, Business Analyst, Architecture

This document describes the first three agents in the orchestrator pipeline.

## Requirements Agent

**Purpose**: Analyze a user request and produce a structured requirements document.

**Input**:
- `request` (str): The user's problem statement or feature request.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "requirements"`, `content` (the generated document), and `source_request`.
- `artifact_name` (str): "requirements_v1"
- `status` (str): "success" or "error"

**Example**:
```python
from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent

orch = Orchestrator()
orth.register_agent(RequirementsAgent())
out = orch.run_agent("requirements", {"request": "Build a todo app"})
print(out["artifact"]["content"])  # Requirements document
```

## Business Analyst Agent

**Purpose**: Analyze requirements and produce user stories, acceptance criteria, and business value assessments.

**Input**:
- `artifact` (dict, optional): The requirements artifact from a prior step.
- `requirements_text` (str, optional): Raw requirements text.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "business_analysis"` and the generated analysis.
- `artifact_name` (str): "business_analysis_v1"
- `status` (str): "success" or "error"

## Architecture Agent

**Purpose**: Design the system architecture based on requirements and business analysis.

**Input**:
- `artifact` (dict, optional): The business analysis artifact from a prior step.
- `requirements_text` (str, optional): Raw requirements text.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "architecture"` and the design document.
- `artifact_name` (str): "architecture_v1"
- `status` (str): "success" or "error"

## Pipeline Execution

The orchestrator chains these agents using `run_pipeline`:

```python
orch = Orchestrator()
orth.register_agent(RequirementsAgent())
orth.register_agent(BusinessAnalystAgent())
orth.register_agent(ArchitectureAgent())

result = orch.run_pipeline(
    ["requirements", "business_analyst", "architecture"],
    context={"request": "Build a real-time document editor"},
)
print(result["artifact"]["content"])  # Architecture design
```

Each agent:
1. Receives the current context (including outputs from prior steps).
2. Orchestrator injects the configured provider.
3. Agent uses the provider to generate content.
4. Agent returns artifact metadata.
5. Orchestrator merges the output back into context and stores artifact in memory.
6. Next agent receives updated context.
