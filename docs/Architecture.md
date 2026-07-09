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

**Planning Agent (current commit)**
- PlanningAgent: architecture → detailed project plan (milestones, phases, tasks, timeline)
- Unit tests for Planning agent
- Full pipeline integration test (Requirements → Analysis → Architecture → Planning)
- Planning agent documentation
- Now supports end-to-end orchestration from request to actionable project plan

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
RequirementsAgent
     ↓ (requirements document)
BusinessAnalystAgent
     ↓ (user stories, acceptance criteria)
ArchitectureAgent
     ↓ (system design)
PlanningAgent
     ↓ (project plan)
Final Artifact: Project Plan
```

## Next Steps

1. **Coding Agent** — Generate source code scaffolds based on architecture and plan
2. **Testing Agent** — Write unit and integration test templates
3. **Documentation Agent** — Generate API docs, guides, release notes
4. **Deployment Agent** — Create CI/CD workflows and deployment scripts
5. **Memory Persistence** — Persist artifacts and conversation state to disk/database
6. **Real Provider SDKs** — Replace stubs with actual OpenAI, Anthropic, Copilot integrations
7. **Parallel Execution** — Extend WorkflowEngine to support concurrent agent runs
8. **Human Approval Steps** — Add gates for approval-required decisions
9. **Logging & Observability** — Structured logging, audit trails, metrics
10. **Error Recovery & Retry Logic** — Improve resilience and retry strategies
