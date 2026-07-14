# Slugger MVP: Idea to Runnable Python Draft PR

The MVP path is Slugger's primary documented capability. It turns one product idea into a small runnable Python CLI project in an isolated workspace, validates the generated files, installs the generated project, runs tests and a smoke command, and publishes the result as one draft GitHub pull request.

## Golden Command

```bash
slugger mvp build \
  "Create a CLI task tracker with add, list, and done commands" \
  --name task-tracker \
  --template cli \
  --repo mightyjoe909/task-tracker \
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