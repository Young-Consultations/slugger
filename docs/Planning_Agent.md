# Planning Agent

This document describes the Planning agent in the orchestrator pipeline.

## Planning Agent

**Purpose**: Translate architecture design into a detailed project plan with milestones, phases, tasks, and timeline estimates.

**Input**:
- `artifact` (dict, optional): The architecture artifact from a prior step.
- `architecture_text` (str, optional): Raw architecture text.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "project_plan"` and the generated plan document.
- `artifact_name` (str): "project_plan_v1"
- `status` (str): "success" or "error"

## Plan Contents

The Planning agent generates a comprehensive project plan including:

1. **Project Overview and Objectives** — High-level goals and scope
2. **Milestones** — Key deliverables and target dates
3. **Project Phases** — Discovery, Design, Development, Testing, Deployment
   - Duration, key activities, deliverables, dependencies for each phase
4. **Work Breakdown Structure** — Tasks and subtasks with effort estimates (story points or days)
5. **Resource Requirements** — Team roles and headcount
6. **Risk Assessment and Mitigation Plan** — Identified risks and mitigation strategies
7. **Success Criteria and KPIs** — Measurable success metrics
8. **Timeline** — Gantt chart description with phase sequencing

## Full Pipeline Example

The Planning agent completes the first half of the orchestration pipeline:

```python
from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.orchestrator.agents.planning import PlanningAgent

orch = Orchestrator()
orth.register_agent(RequirementsAgent())
orth.register_agent(BusinessAnalystAgent())
orth.register_agent(ArchitectureAgent())
orth.register_agent(PlanningAgent())

result = orch.run_pipeline(
    ["requirements", "business_analyst", "architecture", "planning"],
    context={"request": "Build a collaborative document editor"},
)
print(result["artifact"]["content"])  # Detailed project plan
```

## Agent Chaining

The Planning agent receives the architecture artifact from the prior step:

1. **Requirements Agent** generates requirements document
2. **Business Analyst Agent** reads requirements → generates user stories and analysis
3. **Architecture Agent** reads analysis → generates architecture design
4. **Planning Agent** reads architecture → generates project plan

Each agent:
- Receives current context (including outputs from prior steps)
- Orchestrator injects the configured provider
- Agent uses provider to generate content
- Agent returns artifact metadata
- Orchestrator merges output into context and stores artifact in memory
- Next agent receives updated context
