# ADR 0015: Build Command Single-Input Interface

Status: Accepted

## Context

The original CLI `run` subcommand required users to know and specify a workflow
name or YAML path directly.  This created friction for new users who simply want
to take an idea from concept to code without understanding the internal workflow
taxonomy.

The product requirement is to introduce a focused, user-facing entry point where
the user supplies all necessary context in one command invocation:

1. **App idea** — a free-text description of what should be built.
2. **Output platform** — the target delivery environment (iOS, Android, web).
3. **Coding agent** — the AI provider driving code generation (optional; defaults
   to `codex`, `anthropic` also supported).

## Decision

Add a `build` subcommand to the existing CLI (`cli/main.py`) that accepts the
three inputs above as a single, cohesive invocation rather than requiring users
to chain multiple configuration steps.

Introduce the following new domain types in `models/project.py`:

- `Platform` — enum with values `ios`, `android`, `web`.
- `CodingAgent` — enum with values `codex`, `anthropic`.
- `ProjectInput` — dataclass aggregating `idea`, `platform`, and `coding_agent`,
  with an `as_metadata()` helper that projects the values to a plain `dict[str,
  str]` for workflow propagation.

Extend `WorkflowEngine.run()` and `StepExecutor.execute()` with an optional
`metadata` parameter so that the project context is visible to every step's
`ExecutionContext`.

Add `Slugger.build(project_input, workflow=None)` to the orchestrator as the
high-level entry point.  The default workflow is `full-sdlc`; callers may
override it via `--workflow`.

The existing `run`, `list`, and `status` subcommands are preserved unchanged,
ensuring backwards compatibility.

## Alternatives Considered

**Extend the `run` subcommand** with `--idea / --platform / --coding-agent`
flags.  Rejected because `run` is a low-level primitive whose primary concern is
selecting a workflow by name; mixing project-context flags into it would reduce
cohesion and make the interface harder to reason about.

**Interactive prompt (stdin)** — collecting input interactively would reduce
scriptability and CI/CD compatibility.  Rejected in favour of explicit flags.

## Consequences

- Users can initiate a build with a single command: `slugger build "My app"
  --platform ios`.
- `ProjectInput` is the canonical carrier of user intent; agents can inspect
  `context.metadata` for `idea`, `platform`, and `coding_agent` without tight
  coupling.
- Adding new platforms or coding agents requires only a new enum value and a
  corresponding `choices` update in the CLI.
- Backwards compatibility with all existing subcommands is maintained.
