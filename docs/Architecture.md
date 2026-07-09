# Architecture Notes (Updated)

This document reflects the evolution of the orchestrator architecture as agents are added.

## Completed

**Scaffold (commit 866b4142)**
- Agent base interface
- AgentManager for agent registration
- Memory component (project, conversation, decision, prompt, artifact registries)
- WorkflowEngine for sequential execution
- Unit tests
- CI workflow

**Provider Abstraction (commit d2bf55b)**
- AIProvider base interface
- OpenAI, Anthropic, Copilot stubs
- ProviderFactory for instantiation
- ProviderConfig for environment-based configuration
- Provider tests

**Orchestrator Core (commit 4b58f30)**
- Orchestrator class composing AgentManager, Memory, WorkflowEngine
- Provider injection into agent execution
- run_agent() and run_pipeline() methods
- Artifact registration in memory
- Orchestrator tests

**Pipeline Agents (commit 2a7b334)**
- RequirementsAgent: user request → requirements document
- BusinessAnalystAgent: requirements → user stories, acceptance criteria, business value
- ArchitectureAgent: analysis → architecture design
- Agent-specific tests
- Full pipeline integration test (Requirements → Analysis → Architecture)
- Pipeline documentation

**Planning Agent (commit 4f92460)**
- PlanningAgent: architecture → detailed project plan (milestones, phases, tasks, timeline)
- Unit tests for Planning agent
- Full pipeline integration test (Requirements → Analysis → Architecture → Planning)
- Planning agent documentation
- Now supports end-to-end orchestration from request to actionable project plan

**Coding Agent (current commit)**
- CodingAgent: plan → code scaffolds and project structure
- Unit tests for Coding agent
- Full pipeline integration test (Requirements → Analysis → Architecture → Planning → Coding)
- Coding agent documentation
- Now supports complete design-to-code pipeline

## Design Principles Maintained

- **SOLID**: Each agent has a single responsibility; interfaces are clear.
- **Clean/Hexagonal Architecture**: Agents are decoupled from provider implementations.
- **Dependency Injection**: Provider and orchestrator are passed explicitly.
- **Plugin Architecture**: AgentManager allows adding new agents without modifying existing code.
- **Test-Driven**: All new code includes unit and integration tests.
- **Incremental Development**: Each agent added one at a time with full test coverage.

## Current Pipeline State

```
User Request
     ↓
RequirementsAgent (generates requirements document)
     ↓ (artifact passed to next agent)
BusinessAnalystAgent (generates user stories & analysis)
     ↓
ArchitectureAgent (generates system design)
     ↓
PlanningAgent (generates project plan)
     ↓
CodingAgent (generates code scaffolds)
     ↓
Final Artifact: Project Code Structure & Scaffolds
```

## Next Steps

1. **Testing Agent** — Write unit and integration test templates
2. **Documentation Agent** — Generate API docs, guides, release notes
3. **Deployment Agent** — Create CI/CD workflows and deployment scripts
4. **Memory Persistence** — Persist artifacts and conversation state to disk/database
5. **Real Provider SDKs** — Replace stubs with actual OpenAI, Anthropic, Copilot integrations
6. **Parallel Execution** — Extend WorkflowEngine to support concurrent agent runs
7. **Human Approval Steps** — Add gates for approval-required decisions
8. **Logging & Observability** — Structured logging, audit trails, metrics
9. **Error Recovery & Retry Logic** — Improve resilience and retry strategies
10. **Agent Composition** — Enable agents to call other agents (sub-pipelines)
