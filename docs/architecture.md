# Slugger System Architecture
Version: 1.0.0

---

## Purpose

This document provides a comprehensive overview of the Slugger system architecture. It describes the major components, their responsibilities, the layers they belong to, the data flows between them, and the key design patterns applied throughout the system.

This document should be read alongside the [AI-SDLC Specification](ai-sdlc-spec.md) and the [Architecture Decision Records](adr/README.md).

---

## Architectural Vision

Slugger is an **AI Software Factory** — a platform that orchestrates specialized AI agents to execute a complete Software Development Life Cycle (SDLC), producing all artifacts expected from a mature software engineering organization.

Three principles govern every architectural decision:

1. **Extensibility over completeness** — the platform grows through plugins and new agents, not through rewriting the core.
2. **Artifacts over code** — documentation, specifications, and decision records are first-class outputs.
3. **Observability by design** — every action is measurable, inspectable, and auditable.

---

## Architectural Style

Slugger combines three complementary architectural styles:

| Style | Applied To |
|-------|-----------|
| **Clean Architecture** | Core domain isolation; business logic is framework-independent |
| **Hexagonal Architecture** | Provider and external system integration via adapter ports |
| **Plugin Architecture** | Agent, workflow, validator, and provider extensibility |

The combination ensures that:
- Core domain logic is testable in isolation.
- External providers (OpenAI, Anthropic, GitHub) can be swapped without changing core logic.
- New agents and capabilities can be added without modifying existing code.

---

## System Layers

The system is organized into five concentric layers, from innermost to outermost:

```
┌──────────────────────────────────────────────────────────────┐
│                        CLI / API Layer                        │
├──────────────────────────────────────────────────────────────┤
│                     Orchestrator Layer                        │
├──────────────────────────────────────────────────────────────┤
│              Workflow Engine / State Machine Layer            │
├──────────────────────────────────────────────────────────────┤
│                    Agent Execution Layer                      │
├──────────────────────────────────────────────────────────────┤
│           Core Domain / Models / Interfaces Layer             │
└──────────────────────────────────────────────────────────────┘
                              │
              External Adapters (Providers, Services)
```

### Layer 1: Core Domain

**Directory:** `core/`, `models/`

The innermost layer contains domain entities, value objects, interfaces, and business rules. It has no dependencies on external frameworks, databases, or AI providers.

Key contents:
- Domain entities: `Agent`, `Workflow`, `Artifact`, `Step`, `QualityGate`, `Plugin`
- Value objects: `AgentCapability`, `ArtifactMetadata`, `ExecutionContext`
- Repository interfaces: `ArtifactRepository`, `WorkflowRepository`
- Domain events: `WorkflowStarted`, `StepCompleted`, `ArtifactCreated`, `AgentFailed`
- Core exceptions and error types

### Layer 2: Agent Execution

**Directory:** `agents/`

Specialized agents implement domain operations. Each agent follows the agent contract (see [ADR 0008](adr/0008-agent-architecture-design.md)):
- Single responsibility
- Declared capabilities, inputs, outputs, and dependencies
- Lifecycle: `initialize → execute → teardown`
- Communication via artifacts, not direct coupling

Agent categories:
| Category | Responsibility |
|----------|---------------|
| Planning agents | Vision, requirements, user stories |
| Architecture agents | System design, ADRs, component definitions |
| Development agents | Code generation, interface implementation |
| QA agents | Test generation, validation, quality gate evaluation |
| Operations agents | CI/CD, deployment, monitoring |
| Support agents | Documentation, knowledge capture, release notes |

### Layer 3: Workflow Engine / State Machine

**Directory:** `workflow/`, `state_machine/`

The workflow engine interprets declarative YAML workflow definitions and coordinates agent execution. It manages:
- Step sequencing and dependency resolution
- Quality gate evaluation
- Execution state persistence (supports restart and resume)
- Retry policies
- Event emission for observability

The state machine (`state_machine/`) manages per-workflow and per-step lifecycle transitions:
- `PENDING → RUNNING → COMPLETED | FAILED | RETRYING | SKIPPED`

### Layer 4: Orchestrator

**Directory:** `orchestrator/`

The orchestrator is the top-level coordinator. It:
- Receives user intent (project idea, task specification)
- Selects the appropriate workflow
- Invokes the workflow engine
- Aggregates results
- Reports progress and final outcomes

The orchestrator does not contain business logic; it delegates entirely to the workflow engine and agents.

### Layer 5: CLI / API

**Directory:** `cli/` (within `scripts/` initially)

The outermost interface through which users interact with Slugger. The CLI parses user input and translates it into orchestrator invocations. Future phases will add an HTTP API layer for programmatic access and integration.

---

## Cross-Cutting Concerns

The following concerns span all layers and are implemented in dedicated directories:

| Concern | Directory | Description |
|---------|-----------|-------------|
| Observability | `observability/` | Structured logging, execution events, metrics collection |
| Configuration | `config/` | Environment-based configuration, secrets management |
| Plugin Registry | `plugins/` | Agent and provider discovery and registration |
| Knowledge | `knowledge/` | Engineering knowledge base, lessons learned, reusable patterns |
| Memory | `memory/` | Execution context and cross-run knowledge persistence |
| Metrics | `metrics/` | Counters, timers, cost tracking |
| Providers | `providers/` | AI provider adapters (OpenAI, Anthropic, GitHub Copilot, local) |
| Services | `services/` | External service adapters (GitHub, file system, storage) |
| Validators | `validators/` | Input/output validation, quality gate implementations |
| Templates | `templates/` | Document and artifact templates |
| Artifacts | `artifacts/` | Generated artifact storage and retrieval |

---

## Component Diagram

```
User
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLI                                                            │
│  scripts/cli.py                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Orchestrator                                                   │
│  orchestrator/                                                  │
│  • Receives intent                                              │
│  • Selects workflow                                             │
│  • Delegates to workflow engine                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌───────────────────────────┐
│  Workflow Engine │    │  Plugin Registry           │
│  workflow/       │◄───│  plugins/                  │
│                  │    │  • Discovers agents        │
│  • Interprets   │    │  • Discovers providers      │
│    YAML defs    │    │  • Discovers validators     │
│  • Sequences    │    └───────────────────────────┘
│    steps        │
│  • Manages      │
│    state        │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│  State Machine          Observability                          │
│  state_machine/         observability/                         │
│  • Step lifecycle       • Structured logs                      │
│  • Workflow lifecycle   • Execution events                     │
│  • State persistence    • Metrics                              │
└────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Agents                                                          │
│  agents/planning/     agents/architecture/                       │
│  agents/development/  agents/qa/                                │
│  agents/operations/   agents/support/                           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
┌─────────────────┐   ┌───────────────────────────────────────────┐
│  Providers      │   │  Core Domain                              │
│  providers/     │   │  core/ + models/                          │
│  • OpenAI       │   │  • Entities, value objects                │
│  • Anthropic    │   │  • Repository interfaces                  │
│  • GitHub       │   │  • Domain events                          │
│  • Local LLM    │   │  • Business rules                         │
└─────────────────┘   └───────────────────────────────────────────┘
```

---

## Data Flow

### Primary Workflow Execution Flow

```
1. User submits idea via CLI
2. CLI → Orchestrator: CreateProject(idea)
3. Orchestrator → Plugin Registry: SelectWorkflow("sdlc-full")
4. Orchestrator → Workflow Engine: Execute(workflow, context)
5. Workflow Engine → State Machine: Initialize(workflow)
6. For each step in workflow:
   a. Workflow Engine → Plugin Registry: ResolveAgent(step.agent_capability)
   b. Workflow Engine → Agent: Execute(input_artifacts, context)
   c. Agent → Provider: GenerateContent(prompt)
   d. Provider → Agent: Response
   e. Agent → Artifact Repository: Store(output_artifact)
   f. Workflow Engine → Validator: EvaluateQualityGate(step.quality_gate)
   g. Workflow Engine → State Machine: TransitionStep(step, COMPLETED)
   h. Workflow Engine → Observability: Emit(StepCompleted event)
7. Workflow Engine → Orchestrator: WorkflowCompleted(artifacts)
8. Orchestrator → CLI: Present(summary, artifact_paths)
```

### Artifact Communication Pattern

Agents do not call each other directly. They communicate exclusively through artifacts:

```
Agent A → Artifact Repository (write output_artifact)
                   ↓
Workflow Engine reads output_artifact, passes as input to Agent B
                   ↓
Agent B ← Artifact Repository (read input_artifact)
```

This decoupling ensures agents remain independently testable and replaceable.

---

## Provider Abstraction

All AI capabilities are accessed through the `ProviderInterface` defined in `core/`. This abstraction supports multiple backends:

| Provider | Use Case |
|----------|----------|
| OpenAI (GPT-4o, etc.) | Default text generation |
| Anthropic (Claude) | Alternative text generation |
| GitHub Copilot | GitHub-integrated scenarios |
| Local LLM | Air-gapped or cost-sensitive deployments |

Provider selection is configuration-driven. New providers are added as plugins in `providers/` without modifying agent code.

---

## Plugin System

Slugger uses a discovery-based plugin system:

1. On startup, the Plugin Registry scans registered plugin directories.
2. Each plugin declares its type (`agent`, `provider`, `validator`, `workflow`) and metadata.
3. The registry indexes plugins by capability name.
4. The workflow engine and orchestrator look up plugins by capability, not by class name.

This ensures new capabilities can be added by dropping a new module into the appropriate directory and registering it — no core code changes required.

---

## Security Architecture

Security is applied at every layer (see [ADR 0012](adr/0012-security-architecture-principles.md)):

- **Secrets**: sourced from environment variables or a secrets manager, never hardcoded.
- **Input validation**: all workflow definitions, agent inputs, and API payloads are validated before processing.
- **Output sandboxing**: generated code is stored in `artifacts/` for human review; it is never automatically executed.
- **Least privilege**: each provider adapter holds only the credentials required for its function.
- **Audit logging**: all agent invocations, artifact writes, and provider calls are logged with timestamps.

---

## Observability Architecture

Every meaningful event in the system is observable (see [ADR 0011](adr/0011-observability-and-telemetry.md)):

- **Structured logs**: JSON format, written to `logs/`, configurable for external sinks.
- **Execution events**: typed events emitted for each state transition and significant action.
- **Metrics**: counters and timers tracked in `metrics/`; includes token usage and estimated AI cost.
- **Workflow state**: persisted in `state_machine/` to support restart and audit.

---

## Directory Structure Summary

```
slugger/
├── agents/             # Specialized AI agent implementations
│   ├── planning/
│   ├── architecture/
│   ├── development/
│   ├── qa/
│   ├── operations/
│   └── support/
├── artifacts/          # Generated artifact storage
├── config/             # Configuration files and loaders
├── core/               # Domain interfaces, entities, events (no external deps)
├── docs/               # Project documentation (this file lives here)
│   └── adr/            # Architecture Decision Records
├── examples/           # Example workflows and usage
├── knowledge/          # Engineering knowledge base
├── logs/               # Runtime log output
├── memory/             # Cross-run context and knowledge persistence
├── metrics/            # Metrics collection and reporting
├── models/             # Domain model implementations
├── observability/      # Logging, event emission, telemetry
├── orchestrator/       # Top-level workflow coordination
├── plugins/            # Plugin registry and loader
├── prompts/            # System and task prompt library
│   └── system/         # Permanent AI agent operating guidelines
├── providers/          # AI provider adapters
├── scripts/            # CLI entry points and utility scripts
├── services/           # External service adapters (GitHub, filesystem)
├── state_machine/      # Workflow and step lifecycle management
├── templates/          # Document and artifact templates
├── tests/              # Automated test suite
├── validators/         # Input/output validators and quality gate logic
└── workflow/           # Declarative workflow definitions (YAML)
```

---

## Quality and Testing

All behavior-bearing components include:

- **Unit tests** — agent logic, domain rules, validator logic (in `tests/unit/`)
- **Integration tests** — workflow execution with real or stubbed providers (in `tests/integration/`)
- **Validation tests** — quality gate criteria against sample artifacts (in `tests/validation/`)

The test suite follows pytest conventions and lives in `tests/`.

---

## Evolution

This architecture is designed to grow incrementally:

- New AI providers: add a new adapter to `providers/`.
- New agent types: add a new module to `agents/` and register it.
- New workflow patterns: add a YAML definition to `workflow/`.
- New artifact types: extend `models/` and `artifacts/`.
- New programming language support: extend provider abstractions and artifact generators.

No architectural changes are required for these extensions — only additions.

---

## Related Documents

| Document | Path |
|----------|------|
| AI-SDLC Specification | [docs/ai-sdlc-spec.md](ai-sdlc-spec.md) |
| Architecture Decision Records | [docs/adr/README.md](adr/README.md) |
| Repository Context | [prompts/system/RepositoryContext.md](../prompts/system/RepositoryContext.md) |
| Master Orchestrator | [prompts/system/MasterOrchestrator.md](../prompts/system/MasterOrchestrator.md) |
