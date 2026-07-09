# Documentation Agent

This document describes the Documentation agent in the orchestrator pipeline.

## Documentation Agent

**Purpose**: Generate comprehensive project documentation including API docs, guides, deployment procedures, and operational guides.

**Input**:
- `artifact` (dict, optional): The code scaffold artifact from a prior step.
- `code_text` (str, optional): Raw code scaffold text.
- `architecture_text` (str, optional): Raw architecture text.
- `requirements_text` (str, optional): Raw requirements text.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "documentation"` and the generated documentation.
- `artifact_name` (str): "documentation_v1"
- `status` (str): "success" or "error"

## Generated Documentation

The Documentation agent generates comprehensive documentation including:

1. **README.md** — Project overview and quick start
   - Project description and purpose
   - Key features
   - Prerequisites and installation
   - Quick start guide
   - Contributing guidelines

2. **API Documentation** — Endpoint and module documentation
   - API endpoint descriptions
   - Request/response formats
   - Authentication requirements
   - Error codes and handling
   - Code examples

3. **Architecture Documentation** — System design overview
   - System architecture diagrams (ASCII/Mermaid)
   - Component descriptions
   - Data flow diagrams
   - Technology stack details
   - Design patterns and scalability

4. **Setup and Installation Guide** — Step-by-step setup
   - Development environment setup
   - Database setup and migrations
   - Configuration and environment variables
   - Dependency installation
   - Running locally and tests

5. **Deployment Documentation** — Production deployment guide
   - Deployment architecture
   - Pre-deployment checklist
   - Step-by-step deployment process
   - Docker/container deployment
   - Cloud platform setup (AWS, GCP, Azure)
   - Monitoring and logging setup
   - Rollback procedures

6. **User Guide** — How to use the system
   - Feature overview
   - Step-by-step tutorials
   - Common workflows
   - Troubleshooting guide
   - FAQ section

7. **Developer Guide** — For contributors
   - Code organization and structure
   - Development workflow
   - Coding standards
   - Testing guidelines
   - Git workflow
   - Release process

8. **CHANGELOG** — Version history
   - Version releases with dates
   - New features and bug fixes
   - Breaking changes
   - Migration guides
   - Deprecated features

9. **Database Schema Documentation** — Data model reference
   - Entity-relationship diagrams
   - Table descriptions
   - Column definitions and types
   - Relationships and foreign keys
   - Example queries

10. **Operations Guide** — Running in production
    - Monitoring and alerting setup
    - Backup and recovery procedures
    - Performance tuning
    - Security hardening
    - Incident response procedures

## Full Pipeline Example

The Documentation agent extends the orchestration pipeline to include comprehensive documentation:

```python
from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.orchestrator.agents.planning import PlanningAgent
from slugger.orchestrator.agents.coding import CodingAgent
from slugger.orchestrator.agents.testing import TestingAgent
from slugger.orchestrator.agents.documentation import DocumentationAgent

orch = Orchestrator()
orth.register_agent(RequirementsAgent())
orth.register_agent(BusinessAnalystAgent())
orth.register_agent(ArchitectureAgent())
orth.register_agent(PlanningAgent())
orth.register_agent(CodingAgent())
orth.register_agent(TestingAgent())
orth.register_agent(DocumentationAgent())

result = orch.run_pipeline(
    ["requirements", "business_analyst", "architecture", "planning", "coding", "testing", "documentation"],
    context={"request": "Build a collaborative document editor"},
)
print(result["artifact"]["content"])  # Comprehensive documentation
```

## Agent Chaining

The Documentation agent receives the test scaffolds from the prior step:

1. **Requirements Agent** generates requirements document
2. **Business Analyst Agent** reads requirements → generates user stories and analysis
3. **Architecture Agent** reads analysis → generates architecture design
4. **Planning Agent** reads architecture → generates project plan
5. **Coding Agent** reads plan → generates code scaffolds
6. **Testing Agent** reads code → generates test scaffolds
7. **Documentation Agent** reads all prior outputs → generates comprehensive documentation

Each agent:
- Receives current context (including outputs from prior steps)
- Orchestrator injects the configured provider
- Agent uses provider to generate content
- Agent returns artifact metadata
- Orchestrator merges output into context and stores artifact in memory
- Next agent receives updated context

## Generated Documentation Structure

Example documentation structure generated by Documentation agent:

```
docs/
├── README.md (project overview)
├── CHANGELOG.md (version history)
├── SETUP.md (installation and setup)
├── DEPLOYMENT.md (production deployment)
├── USER_GUIDE.md (how to use)
├── API.md (API reference)
├── ARCHITECTURE.md (system design)
├── DEVELOPER_GUIDE.md (contribution guide)
├── DATABASE.md (schema documentation)
├── OPERATIONS.md (running in production)
├── api/
│   ├── users.md
│   ├── documents.md
│   └── ...
├── guides/
│   ├── quick-start.md
│   ├── tutorials.md
│   ├── troubleshooting.md
│   └── faq.md
├── architecture/
│   ├── system-design.md
│   ├── data-flow.md
│   └── diagrams/
└── examples/
    └── code-examples.md
```

Each document includes:
- Markdown formatting with proper headings
- Code examples and snippets
- ASCII or Mermaid diagrams where applicable
- Cross-references between related documentation
- Complete, production-ready content
