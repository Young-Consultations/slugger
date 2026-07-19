⚾ Slugger

The AI Software Factory for turning ideas into runnable Python project drafts.

[![CI](https://github.com/mightyjoe909/slugger/actions/workflows/ci.yml/badge.svg)](https://github.com/mightyjoe909/slugger/actions/workflows/ci.yml)

⸻

What is Slugger?

## Project status for v0.1.1

Current release target: **Slugger v0.1.1**. The canonical user-facing product path is **User idea → Codex generation → validation → isolated installation/tests → restricted verification → generated Git branch → idempotent draft pull request → evidence artifact**.

The user-facing GitHub Actions workflow is **User Idea Codex Slugger MVP Demo** (`.github/workflows/user-idea-codex-cli-demo.yml`). General **CI** is limited to deterministic tests, quality checks, packaging, and golden acceptance tests; it does not publish generated applications. **Canonical Real Codex Slugger MVP Demo** remains an internal, non-user-facing certification workflow for the fixed `hello-codex` scenario.

Required secrets and permissions: `OPENAI_API_KEY` is required only in the protected Codex generation environment. Target validation and the final same-job publication step use `SLUGGER_GITHUB_TOKEN` scoped only to the target repository with Contents read/write, Pull requests read/write, and Metadata read; non-publication jobs remain `contents: read`.

Expected outputs are a sanitized generated Python CLI project, a protected artifact manifest, restricted-verifier evidence, a deterministic `slugger/generated-<project>-<run>` branch, and one draft PR. Publication is skipped/blocked when generation, validation, installation, tests, restricted verification, manifest validation, or path-safety checks fail. Reruns reuse persisted run evidence, deterministic branch naming, and existing draft PR detection to avoid duplicate PRs.

Known limitations: v0.1.1 supports constrained dependency-minimal Python CLI projects; generated code still requires human review; real Codex/GitHub publication requires protected GitHub Actions credentials; broader AI-SDLC packages remain experimental candidates for later extraction in v0.2.0 or later.


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

### User-idea GitHub Actions demo

For a manual GitHub Actions demo that follows the MVP certification flow but lets the operator supply the project idea, run **Actions → User Idea Codex Slugger MVP Demo**. Provide `idea` as the generated CLI concept and `project_name` as a lowercase kebab-case package name other than reserved canonical names such as `hello-codex`; the workflow renders a safe Codex prompt, generates the project in `generated-demo/`, validates it through Slugger, and uploads a reviewable artifact.


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


## Consulting Operating System

Reusable software delivery assessment, reporting, roadmap, and consulting templates are available in [`consulting/`](consulting/README.md).

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

## Real Codex GitHub Actions MVP release path

The single supported MVP release path is the manually triggered workflow `.github/workflows/real-codex-cli-demo.yml`. A new user should follow this path instead of local diagnostic scripts when validating the MVP release. The workflow asks real Codex to generate a small Python CLI demo, validates the generated project, runs tests, runs a deterministic smoke command, and uploads a reviewable artifact.

### What the MVP generates

Codex must create a dependency-minimal Python CLI project in `generated-demo/`:

- project name: `hello-codex`
- package name: `hello_codex`
- required command: `python -m hello_codex.main greet Joseph`
- expected stdout: `Hello, Joseph!`

### Prerequisites

1. Fork or clone this repository on GitHub.
2. Enable GitHub Actions for the repository.
3. Create the protected environment **Settings → Environments → codex-demo**.
4. Add `OPENAI_API_KEY` as an environment secret on `codex-demo`. Do not store it as a repository variable and never commit it.
5. Optionally add a required reviewer to the `codex-demo` environment so the secret-bearing generation job requires approval.

No repository variables are required for the MVP workflow.

### How to run the workflow

1. Open **Actions → Canonical Real Codex Slugger MVP Demo**.
2. Select **Run workflow**.
3. Keep `retain_diagnostics` disabled for normal runs, or enable it to retain failure diagnostics for 14 days.
4. Approve the `codex-demo` environment if your repository requires approval.

### Workflow execution path

The workflow has one primary manual trigger and these jobs:

1. **Prepare deterministic Codex input** renders the fixed prompt.
2. **Generate CLI demo with real Codex** checks that `OPENAI_API_KEY` is configured and invokes `openai/codex-action` without exposing the secret in logs.
3. **Package generated CLI demo** sanitizes the generated files and writes a protected manifest.
4. **Validate generated CLI demo** installs verifier dependencies, imports the artifact through Slugger's artifact adapter, runs generated-project validation, runs unit/integration checks, runs the non-interactive smoke command, verifies the protected manifest, and records sanitized evidence.
5. **Upload success artifact** uploads `slugger-mvp-cli-demo-<run_id>` only when validation succeeds.

Failure paths return non-zero exit codes and upload `slugger-codex-certification-<run_id>` with sanitized logs and evidence when available.

### Downloaded artifact contents

The success artifact contains only review/run material:

- `generated-demo/` source, tests, README, and dependency metadata
- `generated-project-manifest.json`
- `generation-summary.json`
- `verification-evidence.json`
- `slugger-build-summary.json`
- `MVP_ARTIFACT_README.md`

It excludes secrets, virtual environments, caches, `.git`, workflow files, and unrelated repository content.

### Run the generated CLI locally

After downloading and extracting `slugger-mvp-cli-demo-<run_id>`:

```bash
cd generated-demo
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
python -m pytest -q
python -m hello_codex.main greet Joseph
```

Expected successful output:

```text
Hello, Joseph!
```

### Run repository validation locally

Use the same repository checks that CI uses where local tools are available:

```bash
python -m pip install -e '.[test]'
ruff check .
ruff format --check .
python -m mypy mvp cli
python -m compileall .
python -m pytest tests/test_mvp_*.py tests/mvp -q
```

### Common failure conditions

- Missing `OPENAI_API_KEY`: configure it as a `codex-demo` environment secret.
- Pending environment approval: approve the protected `generate-with-codex` job.
- Codex generation error: inspect the Codex action step and diagnostics artifact.
- Invalid generated project: inspect `verification-evidence.json` for the failed validation, install, test, smoke, or mutation-check phase.
- Artifact manifest mismatch: rerun the workflow; do not manually edit files inside the artifact.
- Docker unavailable: GitHub-hosted Ubuntu runners provide Docker; local workflow emulation must provide Docker for container verification.

See [docs/mvp-release-checklist.md](docs/mvp-release-checklist.md) before tagging `v0.1.1`.

### User-idea publication credentials

The canonical user-idea workflow publishes only after validation, isolated install/tests, smoke checks, and restricted container verification pass in the same job. Configure `SLUGGER_GITHUB_TOKEN` as a repository or environment secret for the target validation and final publication steps. The token must be scoped to the target sandbox repository only, with Contents read/write, Pull requests read/write, and Metadata read. `${{ github.token }}` is reserved for Slugger-repository operations and is not used for cross-repository publication.

The verifier image carries `/opt/slugger-wheelhouse` with exact `constraints-ci.txt` versions for `pip`, `setuptools`, `wheel`, and `pytest`; runtime verification installs from that wheelhouse without network access.
