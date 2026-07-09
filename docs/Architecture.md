# Architecture notes for the initial orchestrator scaffold

This document summarises the initial scaffold added on branch feature/init-try1.

Goals
- Provide small, well-typed abstractions for Agents and AI Providers.
- Introduce a Memory component to hold project and conversation state.
- Add a minimal WorkflowEngine that supports sequential execution and retries.
- Provide an AgentManager registry for deterministic agent registration.
- Include unit tests and a CI job to run them.

Design principles followed
- SOLID: single-responsibility classes and clear interfaces.
- Clean/Hexagonal: separation between provider adapters and orchestrator core.
- Dependency injection: components are instantiated and passed explicitly in tests.
- Plugin architecture: AgentManager serves as a simple registry; future work will add dynamic discovery.

Next steps
- Implement provider SDK integrations (OpenAI, Anthropic, Copilot).
- Extend AgentManager with plugin discovery (importlib / entry points).
- Implement memory persistence and a knowledge-base index.
- Build the orchestration pipeline connecting Requirements->Planning->Coding->Testing agents.
- Add logging, retry policies, human approval steps, parallel workflow execution and better error handling.

