# Domain Model

Slugger models an AI software factory as a set of collaborating domain entities centered on workflows, artifacts, and specialized agents. The domain model is intentionally artifact-first: every meaningful action consumes or produces a traceable artifact.

## Core Entities

### Project
Represents the software initiative currently being executed by Slugger. A project owns goals, constraints, stakeholders, lifecycle phase, and the set of workflows executed on its behalf.

### Workflow
A declarative description of how Slugger executes a repeatable delivery process. A workflow defines ordered steps, recovery behavior, quality gates, and expected artifacts.

### WorkflowStep
The smallest executable unit in a workflow. A step binds one capability-focused agent to explicit inputs, outputs, retry rules, and quality gates.

### Agent
An autonomous worker with a single responsibility. Agents consume structured context and artifacts, perform focused reasoning or automation, and emit new artifacts.

### AgentCapability
A formal declaration describing what an agent can do, which artifact types it understands, and which outcomes it can produce.

### Artifact
The canonical unit of communication between agents. Artifacts represent specifications, architecture documents, source code, tests, deployment assets, review notes, and operational evidence.

### ArtifactType
A taxonomy that classifies artifacts into stable categories such as document, code, test, config, and diagram. Artifact type drives validation, routing, and workflow contracts.

### Provider
A pluggable AI or infrastructure dependency used by an agent. Providers abstract model completion, embeddings, GitHub interaction, or future execution backends.

### Plugin
An extension package that contributes agents, validators, providers, workflow recipes, or knowledge packs without modifying the core runtime.

### Memory
A retrievable store of project- or organization-level facts learned during execution. Memory supports continuity, reflection, and context reuse.

### KnowledgeEntry
A curated piece of reusable knowledge such as standards, design patterns, lessons learned, or prompt guidance.

### QualityGate
A policy checkpoint that validates artifacts or execution state before a workflow advances.

### ExecutionContext
The runtime envelope passed into agents and engines. It contains project identity, active step, prior artifacts, execution metadata, and correlation identifiers.

## Entity Relationships

- A **Project** owns one or more **Workflows**.
- A **Workflow** contains an ordered collection of **WorkflowSteps**.
- Each **WorkflowStep** targets exactly one primary **Agent** and may invoke one or more **QualityGates**.
- An **Agent** declares one or more **AgentCapabilities**.
- A **WorkflowStep** consumes and produces **Artifacts** of explicit **ArtifactTypes**.
- **Artifacts** carry provenance linking them back to their source **Agent**, **WorkflowStep**, and **Project**.
- **Providers** are resolved by agents through configuration and dependency injection.
- **Plugins** can register new **Agents**, **Providers**, **Validators**, workflow recipes, or **KnowledgeEntries**.
- **Memory** stores selected **Artifacts** or distilled facts extracted from them.
- **KnowledgeEntries** inform prompts, validation, and agent behavior.
- **ExecutionContext** references the active **Project**, **Workflow**, **WorkflowStep**, artifacts, and execution telemetry.

## Aggregates

### Project Aggregate
Root: `Project`

Contains project metadata, lifecycle state, linked workflow identifiers, and high-level delivery outcomes. Consistency rules such as allowed phase transitions belong here.

### Workflow Aggregate
Root: `Workflow`

Contains workflow metadata, steps, retry policies, and quality gates. The workflow aggregate ensures step sequencing remains internally valid.

### Artifact Aggregate
Root: `Artifact`

Contains artifact metadata, status, classification, and version lineage. Traceability and publication rules are enforced at this boundary.

### Agent Aggregate
Root: `AgentMetadata`

Encapsulates capabilities, provider requirements, supported inputs/outputs, and lifecycle state for a runnable agent.

## Bounded Contexts

### Orchestration Context
Concerned with workflow execution, state transitions, retries, and agent dispatch.

### Agent Runtime Context
Concerned with agent contracts, capabilities, provider usage, and artifact production.

### Artifact Management Context
Concerned with artifact identity, storage, retrieval, provenance, and validation.

### Knowledge and Memory Context
Concerned with reusable knowledge, historical execution memory, and reflective learning.

### Extensibility Context
Concerned with dynamic registration of plugins, providers, validators, and recipes.

### Observability Context
Concerned with events, spans, metrics, and system health generated during execution.
