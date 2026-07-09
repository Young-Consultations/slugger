# Coding Agent

This document describes the Coding agent in the orchestrator pipeline.

## Coding Agent

**Purpose**: Generate source code scaffolds and project structure based on architecture design and project plan.

**Input**:
- `artifact` (dict, optional): The project plan artifact from a prior step.
- `plan_text` (str, optional): Raw project plan text.
- `architecture_text` (str, optional): Raw architecture text.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "code_scaffold"` and the generated code scaffolds.
- `artifact_name` (str): "code_scaffold_v1"
- `status` (str): "success" or "error"

## Generated Code Scaffolds

The Coding agent generates comprehensive code scaffolds including:

1. **Project Structure** — Directory layout and file organization
2. **Technology Stack Setup** — Package managers, dependencies, configuration files (package.json, requirements.txt, pom.xml, etc.)
3. **Core Modules** — Main application files with boilerplate code
4. **API/Controller Layer** — Endpoint definitions and request handlers
5. **Service Layer** — Business logic service classes
6. **Data Access Layer** — Database models and repository patterns
7. **Configuration** — Environment configs, feature flags, settings
8. **Utilities** — Helper functions, logging, error handling
9. **Entry Point** — Main application startup file
10. **Build/Deploy Scripts** — Makefile, Docker setup, CI/CD hooks

For each major component, the agent provides:
- File path and name
- Code skeleton (imports, class/function signatures, docstrings)
- Key implementation notes and TODOs

## Full Pipeline Example

The Coding agent extends the orchestration pipeline to include code generation:

```python
from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.orchestrator.agents.planning import PlanningAgent
from slugger.orchestrator.agents.coding import CodingAgent

orch = Orchestrator()
orth.register_agent(RequirementsAgent())
orth.register_agent(BusinessAnalystAgent())
orth.register_agent(ArchitectureAgent())
orth.register_agent(PlanningAgent())
orth.register_agent(CodingAgent())

result = orch.run_pipeline(
    ["requirements", "business_analyst", "architecture", "planning", "coding"],
    context={"request": "Build a collaborative document editor"},
)
print(result["artifact"]["content"])  # Code scaffolds
```

## Agent Chaining

The Coding agent receives the project plan from the prior step:

1. **Requirements Agent** generates requirements document
2. **Business Analyst Agent** reads requirements → generates user stories and analysis
3. **Architecture Agent** reads analysis → generates architecture design
4. **Planning Agent** reads architecture → generates project plan
5. **Coding Agent** reads plan → generates code scaffolds and project structure

Each agent:
- Receives current context (including outputs from prior steps)
- Orchestrator injects the configured provider
- Agent uses provider to generate content
- Agent returns artifact metadata
- Orchestrator merges output into context and stores artifact in memory
- Next agent receives updated context

## Generated Artifacts

Example output structure from Coding agent:

```
Project Structure:
├── src/
│   ├── main.py (or index.js, etc.)
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── document_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── errors.py
├── tests/
│   ├── unit/
│   └── integration/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt (or package.json, etc.)
├── Makefile
└── README.md
```

Each file includes code skeleton with:
- Import statements
- Class and function signatures
- Docstrings
- Key TODOs and implementation notes
