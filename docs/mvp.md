## Project status for v0.1.2

Current release target: **Slugger v0.1.2**. Slugger documents exactly three distinct operational paths:

1. **User-facing generation workflow — User Idea Codex Slugger MVP Demo** (`.github/workflows/user-idea-codex-cli-demo.yml`): accepts a user idea, generates a constrained Python CLI, validates and verifies it, and opens a draft PR in the separate `Young-Consultations/slugger-generated-demos` repository.
2. **Certification workflow — Canonical Real Codex Slugger MVP Demo** (`.github/workflows/real-codex-cli-demo.yml`): runs the fixed deterministic certification scenario and produces release evidence; it is not the normal user-facing workflow.
3. **Release workflow** (`.github/workflows/release.yml`): validates release evidence, builds the package, and creates the version tag and GitHub Release.

General **CI** is limited to deterministic tests, quality checks, packaging, and golden acceptance tests; it does not publish generated applications.

Required secrets and permissions: `OPENAI_API_KEY` is required only in the protected Codex generation environment. Target validation and the final same-job publication step use `SLUGGER_GITHUB_TOKEN` scoped only to the target repository with Contents read/write, Pull requests read/write, and Metadata read; non-publication jobs remain `contents: read`.

Expected outputs are a sanitized generated Python CLI project, a protected artifact manifest, restricted-verifier evidence, a deterministic `slugger/generated-<project>-<stable-identity-prefix>` branch, and at most one Slugger-managed draft PR per logical request. Publication is skipped/blocked when generation, validation, installation, tests, restricted verification, manifest validation, or path-safety checks fail. Reruns use a stable publication identity independent of workflow and Slugger run IDs, validate machine-readable PR ownership markers, safely migrate a matching legacy run-ID draft PR, update the existing branch/PR with latest verified output, remove stale Slugger-owned generated files, recover safely from create races, and fail closed when duplicate matching drafts or mismatched PR markers are detected.

Known limitations: v0.1.2 supports constrained dependency-minimal Python CLI projects; generated code still requires human review; real Codex/GitHub publication requires protected GitHub Actions credentials; broader AI-SDLC packages remain experimental candidates for later extraction in v0.2.0 or later.

# Slugger MVP: Idea to Runnable Python Draft PR

The MVP path is Slugger's primary documented capability. It turns one product idea into a small runnable Python CLI project in an isolated workspace, validates the generated files, installs the generated project, runs tests and a smoke command, and publishes the result as one draft GitHub pull request.

## Golden Command

```bash
slugger mvp build \
  "Create a CLI task tracker with add, list, and done commands" \
  --name task-tracker \
  --template cli \
  --repo Young-Consultations/task-tracker \
  --base main
```

## Prerequisites

* Python 3.11 or newer.
* Slugger installed from the repository checkout:

  ```bash
  python -m pip install -e .
  ```

* Codex CLI or the supported Codex SDK integration configured for the account that should generate code.
* Git available on `PATH`.
* GitHub CLI (`gh`) available on `PATH` and authenticated.
* GitHub credentials that can read the target repository, create a branch, push commits, and open draft pull requests.
* A target GitHub repository in `owner/repository` form.

Canva, the legacy full workflow engine, legacy agents, approval services, readiness services, and release automation are not prerequisites for the MVP command.

## What the MVP Command Does

The command performs one narrow execution path:

1. Creates a persisted MVP run.
2. Creates an isolated workspace under `.slugger/workspaces/<run-id>/`.
3. Invokes Codex inside that workspace with a versioned Python-project prompt.
4. Inventories generated files and records SHA-256 checksums.
5. Validates required files, safe paths, safe content, Python syntax, package layout, and `pyproject.toml`.
6. Creates a generated-project virtual environment at `<workspace>/.venv`.
7. Installs the generated project with `pip install -e ".[test]"`.
8. Runs generated tests with `pytest -q`.
9. Runs a CLI smoke check with `python -m <package>.main --help`.
10. Creates one GitHub branch for the run.
11. Pushes only generated-project files.
12. Opens one draft pull request and returns the PR URL.

Publication is blocked unless validation, installation, tests, and smoke checks all pass.

## Result Summary

The CLI returns a clear structured summary containing:

* run ID;
* final status;
* workspace path;
* generated-file count;
* validation result;
* test result;
* smoke result;
* GitHub branch;
* draft PR URL;
* error details when the run fails.

## Architecture

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

### Component Responsibilities

* **Workspace manager** — creates approved, run-specific workspaces and rejects traversal, absolute generated paths, repository-root workspaces, and escaping symlinks.
* **Codex adapter** — runs the supported Codex integration only inside the assigned workspace, uses an allowlisted environment, records prompt evidence, and never substitutes static fallback output.
* **Project validator** — validates file presence, path safety, content safety, Python syntax, package name, and `pyproject.toml` before installation or publication.
* **Basic runner** — creates a dedicated virtual environment, installs the generated project, runs generated tests, and runs a CLI smoke command with bounded subprocess output.
* **Run repository** — persists run state, evidence, results, errors, GitHub branch, and PR URL without using legacy workflow persistence.
* **GitHub publisher** — creates one branch and one draft PR per successful run, and returns the existing PR for repeated publication attempts.

## Architecture Boundary

MVP code must not depend on the full-SDLC workflow path. The architecture test prevents `mvp/` imports from prohibited legacy packages, including workflow engine, legacy agent registry, Canva integrations, approval services, readiness services, and release agents.

The broad full-SDLC system is currently experimental. It remains in the repository for research and future design work, but the MVP command is the primary build path.

## Failure Recovery

* **Codex failure** — inspect the run error and preserved workspace; re-run after fixing Codex configuration or prompt/runtime issues.
* **Validation failure** — inspect structured validation checks and generated files in the preserved workspace; GitHub publication will not occur.
* **Install/test/smoke failure** — inspect runner phase output in the run result and the generated workspace; GitHub publication will not occur.
* **GitHub failure** — validation and test evidence remain persisted with the workspace; fix credentials, repository access, or branch/PR conflicts and retry publication for the same run when supported.
* **Duplicate publication attempt** — successful runs are idempotent; repeated publication for the same run returns the existing draft PR instead of creating another one.

Failed workspaces are intentionally preserved for diagnosis. Clean them up explicitly only after collecting evidence you still need.

## Operations Checklist

Before running the MVP command:

- [ ] Confirm Python 3.11+ is active.
- [ ] Install Slugger with `python -m pip install -e .`.
- [ ] Confirm `slugger mvp build --help` works.
- [ ] Confirm Codex authentication and CLI/SDK availability.
- [ ] Confirm `git` is available.
- [ ] Confirm `gh auth status` succeeds for the target GitHub account.
- [ ] Confirm the target repository exists and the base branch is correct.
- [ ] Confirm the working checkout does not contain unrelated changes.

After a run:

- [ ] Review the validation, test, and smoke summaries.
- [ ] Review the generated-file inventory.
- [ ] Open the draft PR URL and inspect the generated code before marking it ready for review.
- [ ] Preserve or clean up the workspace according to debugging needs.

## Milestone Definition of Done

* All MVP child issues are complete.
* The golden task-tracker scenario passes from a clean installation.
* The generated project installs and runs.
* One draft GitHub pull request is created.
* Failed validation never publishes to GitHub.
* Repeating publication for the same run does not create another PR.
* Codex cannot modify the Slugger source repository.

## Known Limitations

* Only the `cli` template is initially supported.
* FastAPI and other application templates are out of scope until the CLI path works reliably.
* The MVP path does not run the full legacy SDLC workflow.
* Canva, design generation, requirements agents, architecture agents, approval workflows, remediation agents, production-readiness scoring, deployment, releases, SBOM, and provenance are out of scope.
* Generated projects are opened as draft PRs and require human review before they should be merged.
* The MVP validates and tests generated Python projects, but it is not a substitute for a full product security review.

## MVP runtime home

The focused MVP path stores runtime data under a single runtime home and never defaults to the source repository or an installed package directory. Resolution order is:

1. `SLUGGER_HOME`, when set.
2. A platform user-data directory (`$XDG_DATA_HOME/slugger` or `~/.local/share/slugger` on Linux, `~/Library/Application Support/Slugger` on macOS, and `%LOCALAPPDATA%\\Slugger` or `%APPDATA%\\Slugger` on Windows).
3. A development fallback of `~/.slugger` only if a platform home cannot be resolved.

The runtime home layout is:

```text
$SLUGGER_HOME/
├── workspaces/
├── state/
│   └── mvp_runs.sqlite3
└── logs/
```

The `slugger mvp build` diagnostic JSON includes `runtime`, `workspace_root`, and `sqlite_path` fields so operators can verify that generated workspaces and SQLite state are outside both the repository and `site-packages`.

## Real Codex proof evidence

The production adapter is fail-closed: when `codex` is unavailable or exits unsuccessfully, the MVP run is marked failed, the workspace is preserved, validation/testing/publication are skipped, and no static fallback project is generated. Real Codex execution must be run with `SLUGGER_MVP_SKIP_PUBLISH=1` when the proof is intended to stop after generated-project installation, pytest, and smoke testing.

Required proof command shape:

```bash
SLUGGER_MVP_SKIP_PUBLISH=1 slugger mvp build \
  "Create a CLI task tracker with add, list, and done commands" \
  --name task-tracker \
  --template cli \
  --repo owner/task-tracker
```

Record the Codex version, Codex session ID, prompt hash, workspace path, generated inventory, installation result, pytest result, CLI smoke result, and source-tree change check from the run JSON and persisted SQLite state.

## Coding-agent lesson learned

Using GitHub Agents as the primary coding agent was not effective for this project. The agents often completed narrowly interpreted tasks without fully integrating the changes, validating the end-to-end execution path, or accurately identifying remaining work. This resulted in repeated cycles of implementation, review, defect discovery, and rework.

Codex has proven more reliable for the current development approach. It has produced more focused changes, responded better to detailed acceptance criteria, and moved the MVP forward more quickly.

For the remainder of the Slugger MVP:

* Codex will be the preferred coding agent.
* GitHub will remain the source-control, pull-request, issue-tracking, and CI platform.
* Work will be divided into small, testable Codex tasks.
* Completion will be based on executable acceptance evidence rather than agent-reported status.
* Human and independent AI review will remain required before merging significant changes.

This conclusion applies to the experience of developing Slugger and does not imply that GitHub Agents are unsuitable for every project or task.

## v0.1.1 verifier and publication updates

The user-idea workflow now keeps publication in the same GitHub Actions job that performs restricted verification. `SLUGGER_HOME` stays under `runner.temp`, so the SQLite run record and generated workspace path remain valid without uploading a runtime-home copy between jobs. Only target validation and final publication receive `secrets.SLUGGER_GITHUB_TOKEN`; generated code, tests, package installation, and Docker verification run without that token.

`SLUGGER_GITHUB_TOKEN` must be a fine-grained PAT or GitHub App installation token scoped only to the configured target repository with Contents read/write, Pull requests read/write, and Metadata read. The workflow validates the target repository and default/base branch before Codex generation starts. The target must be empty or already Slugger-managed for the same deterministic run according to the publisher policy; closed or merged PRs are not duplicated and require the documented rerun/recovery policy before reuse.

Restricted verification uses the offline wheelhouse at `/opt/slugger-wheelhouse`. The Docker image downloads exact wheels from `constraints-ci.txt` at image build time, and the generated-project venv installs `pip`, `setuptools`, `wheel`, and `pytest` with `--no-index`, `--find-links`, and the same constraints. Missing wheelhouse entries produce a controlled provisioning failure instead of copying host site-packages or creating a synthetic build backend.

The success artifact is intentionally small: `generated-demo/`, `generated-project-manifest.json`, `generation-summary.json`, `verification-evidence.json`, `publication-summary.json`, and `MVP_ARTIFACT_README.md`. Runtime homes, virtual environments, caches, temporary Git data, complete logs, and environment dumps are excluded.
