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

### Local Codex demo

For a local-only end-to-end demo that uses the real Codex CLI and intentionally skips GitHub publication, see [docs/codex-demo.md](docs/codex-demo.md). The demo command is:

```bash
./scripts/run_codex_demo.sh
```


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

### Slugger MVP runtime state

The MVP path resolves runtime state through `mvp.runtime_paths` instead of writing beside package files. Set `SLUGGER_HOME` to choose an explicit runtime home; otherwise Slugger uses the current platform's user-data directory and falls back to `~/.slugger` for development-only environments. The layout is `workspaces/`, `state/mvp_runs.sqlite3`, and `logs/`. MVP CLI diagnostics print the resolved workspace root and SQLite path.

## Real Codex CLI demo workflow

The repository includes a manually triggered workflow, `.github/workflows/real-codex-cli-demo.yml`, that demonstrates a real `openai/codex-action@v1` generation followed by a separate credential-free verification job. The generated demo is a Python CLI application only; the workflow does not publish, push, or open a pull request for generated application code by default.

Required setup:
1. Configure **Repository Settings → Environments → codex-demo**.
2. Add a required reviewer for the `codex-demo` environment.
3. Add `OPENAI_API_KEY` as an **environment secret** on `codex-demo`; do not make it a repository-wide environment variable.
4. Start **Actions → Canonical Real Codex Slugger MVP Demo → Run workflow**. The deterministic request is fixed to `hello-codex` / `hello_codex`.

Expected artifact:
- `slugger-codex-certification-<run_id>`: sanitized `certification-summary.json`, `verification-evidence.json`, and `generated-project-manifest.json`, retained for 14 days.

Security boundaries: only the protected `generate-with-codex` job receives `OPENAI_API_KEY`, passed directly to the Codex action as `openai-api-key`. The verification job checks out with `persist-credentials: false`, downloads the artifact, verifies the SHA-256 JSON manifest, imports only manifested files through `ArtifactMvpCodexAdapter` into the existing `DefaultMvpBuildService`, persists a `MvpRun`, independently checks `python -m hello_codex.main greet Joseph`, runs restricted container verification, and uploads bounded certification evidence. Outbound dependency installation is intentionally constrained by requiring a dependency-minimal project and rejecting unsafe package metadata. A Python virtual environment is not a sandbox; the workflow separates credential-bearing generation from generated-code execution and the verification service uses a disposable execution copy for mutation detection.

Troubleshooting:
- Missing secret or pending approval: configure `OPENAI_API_KEY` as a `codex-demo` environment secret and approve the protected environment run.
- Codex-action failure: inspect the generation summary and the Codex action logs; no generated project artifact is trusted unless a manifest is produced.
- Artifact-integrity failure: the verification job rejects missing, extra, modified, symlinked, or mode-changed files before execution.
- Validation failure: review `validator_results` in `verification-evidence.json`.
- Packaging failure: ensure `pyproject.toml` uses `setuptools.build_meta` with no custom backend, path, URL, Git, or index configuration.
- Test failure: review the bounded `run_tests` excerpts in evidence.
- Smoke-test failure: confirm `python -m <package>.main --help` prints help including usage and the project name.
- Container or Docker failure: the current local verifier uses a disposable execution copy; if the GitHub runner Docker service is unavailable, keep verification credential-free and inspect evidence.
