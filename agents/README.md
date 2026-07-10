# agents/

This directory contains all specialized AI agents used by the Slugger orchestration system.

## Purpose

Each agent is responsible for one well-defined task within the AI-SDLC workflow. Agents consume artifacts as inputs, perform focused work, and produce artifacts as outputs.

## Conventions

- One agent per file or subdirectory.
- Each agent declares its capabilities, dependencies, expected inputs, and expected outputs.
- Agents communicate through shared artifacts rather than direct coupling.
- Agent metadata (name, version, description, provider, external interface) is exposed in a standard format.
- `provider` identifies the runtime backend; `external_interface` identifies any role-specific third-party platform contract.

## Default External Interfaces

- `code_generator_agent` — `openai_codex`
- `diagram_agent` — `canva`
- `ci_cd_agent` — `github_actions`

## Examples of Agents

- `requirements_agent` — extracts and formalizes requirements from a product brief
- `architecture_agent` — produces architecture documents and diagrams
- `code_agent` — generates source code from specifications
- `test_agent` — generates unit and integration tests
- `review_agent` — performs code and artifact review
- `documentation_agent` — produces technical documentation

## Related

- `orchestrator/` — coordinates agent execution
- `workflow/` — defines the order and conditions for agent invocations
- `plugins/` — optional plug-in agents discovered at runtime
