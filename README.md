⚾ Slugger

The AI Software Factory for turning ideas into runnable Python project drafts.

[![CI](https://github.com/mightyjoe909/slugger/actions/workflows/ci.yml/badge.svg)](https://github.com/mightyjoe909/slugger/actions/workflows/ci.yml)

⸻

What is Slugger?

Slugger is an open, extensible, Python-based AI Software Factory. Its primary supported path is the MVP build command: give Slugger one idea for a small Python CLI project and it creates an isolated workspace, asks Codex to generate the project, validates the output, installs it in its own virtual environment, runs tests and a CLI smoke check, and opens one draft GitHub pull request with the generated files.

The broader multi-agent AI-SDLC system remains in the repository as an experimental research path. It is not required to run the MVP command and is not the primary documented build flow.

⸻

## Primary MVP Path

The recommended command is:

```bash
slugger mvp build \
  "Create a CLI task tracker with add, list, and done commands" \
  --name task-tracker \
  --template cli \
  --repo mightyjoe909/task-tracker \
  --base main
```

The MVP path performs this narrow flow:

Idea
→ isolated workspace
→ Codex generation
→ validation
→ dedicated virtualenv installation
→ pytest execution
→ CLI smoke check
→ GitHub branch
→ draft pull request

A successful run returns a structured terminal summary with the run ID, final status, workspace path, generated-file count, validation/test/smoke results, GitHub branch, and draft PR URL.

### Prerequisites

* Python 3.11 or newer.
* The Codex CLI or supported Codex SDK integration available to the Slugger process.
* Git and GitHub CLI (`gh`) configured for the target repository.
* GitHub credentials with permission to create branches and draft pull requests.
* A target GitHub repository in `owner/repository` form.

See [docs/mvp.md](docs/mvp.md) for setup, failure recovery, architecture, operations, and known limitations.

⸻

## Installation

Install Slugger in editable mode from a clean checkout:

```bash
python -m pip install -e .
```

Then verify the CLI is available:

```bash
slugger --help
slugger mvp build --help
```

⸻

## MVP Architecture

The MVP command intentionally avoids the legacy full-SDLC workflow engine. The dependency flow is:

```text
CLI
→ MvpBuildService
   → RunRepository
   → WorkspaceManager
   → CodexAdapter
   → ProjectValidator
   → BasicRunner
   → GitHubPublisher
```

MVP code lives under `mvp/` and is guarded by an architecture test that prevents imports from prohibited legacy workflow, agent, approval, readiness, Canva, and release packages.

⸻

## Experimental Full-SDLC System

Slugger still contains a broader AI-SDLC implementation with agents, recipes, workflow orchestration, provider abstractions, knowledge tooling, and design integrations. That system is experimental while the MVP path is being delivered. It is useful for research and future Slugger V2 design, but it is not required for the primary MVP command.

Exploratory commands remain available for contributors who are intentionally working on the experimental path:

```bash
slugger list agents
slugger list workflows
slugger run full-sdlc-v2
slugger status
```

Feature work for the MVP should not be added to `full-sdlc-v2` or the legacy workflow engine.

⸻

## Guiding Principles

Slugger is built around:

* isolated generated-project workspaces;
* explicit validation before installation or publication;
* dedicated generated-project virtual environments;
* structured run persistence independent of legacy workflow persistence;
* draft-only GitHub publication after validation and tests pass;
* versioned prompts and auditable generation evidence;
* strict boundaries between MVP code and experimental legacy systems.

⸻

## Long-Term Vision

The long-term vision remains an AI Software Factory capable of producing complete, traceable software systems while following professional engineering practices. The current product focus is intentionally narrower: make the idea-to-runnable-Python-project MVP reliable before expanding scope.

⸻

## Continuous Integration

GitHub Actions runs the project's CI workflow on pushes to `main` and on pull requests.

The workflow:

- Sets up Python 3.11
- Installs project dependencies
- Runs the test suite with `python -m pytest tests/`

⸻

## Contributing

Contributions are welcome. MVP work should be delivered in focused pull requests, include tests, preserve the `mvp/` architecture boundary, and avoid unrelated full-SDLC functionality.

⸻

## License

This project is licensed under the MIT License.
