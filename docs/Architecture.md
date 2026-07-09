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

**Pipeline Agents (current commit)**
- RequirementsAgent: user request → requirements document
- BusinessAnalystAgent: requirements → user stories, acceptance criteria, business value
- ArchitectureAgent: analysis → architecture design
- Agent-specific tests
- Full pipeline integration test (Requirements → Analysis → Architecture)
- Pipeline documentation

## Design Principles Maintained

- **SOLID**: Each agent has a single responsibility; interfaces are clear.
- **Clean/Hexagonal Architecture**: Agents are decoupled from provider implementations.
- **Dependency Injection**: Provider and orchestrator are passed explicitly.
- **Plugin Architecture**: AgentManager allows adding new agents without modifying existing code.
- **Test-Driven**: All new code includes unit and integration tests.

## Next Steps

1. **Planning Agent** — Translate architecture into a detailed project plan (milestones, tasks).
2. **Coding Agent** — Generate source code scaffolds based on architecture.
3. **Testing Agent** — Write unit and integration tests.
4. **Documentation Agent** — Generate API docs, guides, release notes.
5. **Deployment Agent** — Create CI/CD workflows and deployment scripts.
6. **Memory Persistence** — Persist artifacts and conversation state to disk/database.
7. **Real Provider SDKs** — Replace stubs with actual OpenAI, Anthropic, Copilot integrations.
8. **Parallel Execution** — Extend WorkflowEngine to support concurrent agent runs.
9. **Human Approval Steps** — Add gates for approval-required decisions.
10. **Logging & Observability** — Structured logging, audit trails, metrics.
