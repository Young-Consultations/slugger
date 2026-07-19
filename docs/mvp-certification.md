## Project status for v0.1.1

Current release target: **Slugger v0.1.1**. The canonical user-facing product path is **User idea → Codex generation → validation → isolated installation/tests → restricted verification → generated Git branch → idempotent draft pull request → evidence artifact**.

The user-facing GitHub Actions workflow is **User Idea Codex Slugger MVP Demo** (`.github/workflows/user-idea-codex-cli-demo.yml`). General **CI** is limited to deterministic tests, quality checks, packaging, and golden acceptance tests; it does not publish generated applications. **Canonical Real Codex Slugger MVP Demo** remains an internal, non-user-facing certification workflow for the fixed `hello-codex` scenario.

Required secrets and permissions: `OPENAI_API_KEY` is required only in the protected Codex generation environment. Target validation and the final same-job publication step use `SLUGGER_GITHUB_TOKEN` scoped only to the target repository with Contents read/write, Pull requests read/write, and Metadata read; non-publication jobs remain `contents: read`.

Expected outputs are a sanitized generated Python CLI project, a protected artifact manifest, restricted-verifier evidence, a deterministic `slugger/generated-<project>-<run>` branch, and one draft PR. Publication is skipped/blocked when generation, validation, installation, tests, restricted verification, manifest validation, or path-safety checks fail. Reruns reuse persisted run evidence, deterministic branch naming, and existing draft PR detection to avoid duplicate PRs.

Known limitations: v0.1.1 supports constrained dependency-minimal Python CLI projects; generated code still requires human review; real Codex/GitHub publication requires protected GitHub Actions credentials; broader AI-SDLC packages remain experimental candidates for later extraction in v0.2.0 or later.

# Slugger MVP Certification Evidence

Status: **not 100% certified in this environment**. Offline MVP acceptance, package build, and recoverable publication code paths are evidenced here. Real Codex generation, real GitHub sandbox publication, and green protected CI require credentials and repository administrator controls that were not available to this local agent run.

## Scope

Controlling scope is GitHub issue #24 and the MVP-001 through MVP-011 focused path. The first MVP release supports publishing only to an empty target repository or a repository already Slugger-managed for the same persisted run. Merging generated applications into arbitrary existing Python repositories remains out of scope.

## Local certification fields

| Field | Evidence |
| --- | --- |
| Commit SHA | Filled by release manager after final commit for this branch. |
| Python version | To be captured with `python --version` during final validation. |
| Codex version | Not executed in this environment; capture with `codex --version` in the protected integration environment. |
| GitHub tooling | Production publisher uses `git` and GitHub CLI `gh`; capture `git --version` and `gh --version` in the protected integration environment. |
| Wheel filename/checksum | To be captured after `python -m build` with `sha256sum dist/*.whl`. |
| Runtime-state path | Slugger MVP runtime state is resolved through `mvp.runtime_paths` and verified outside site-packages by CI package verification. |
| Real Codex run/session ID | Not executed here; required before issue #24 closure. |
| Real GitHub sandbox PR URL | Not executed here; required before issue #24 closure. |
| Generated inventory hash | Persisted as `MvpRun.inventory.inventory_hash` and included in draft PR content. |
| Installation evidence | `install_project` check in persisted run test results and draft PR body. |
| Pytest evidence | `run_tests` check in persisted run test results and draft PR body. |
| CLI smoke evidence | `cli_smoke` check in persisted run test results and draft PR body. |
| Idempotency evidence | Publisher reuses deterministic branch/open PR and fake acceptance proves repeat publication returns the same PR. |
| Restart/recovery evidence | `slugger mvp publish <run-id>` and `slugger mvp resume <run-id>` load persisted evidence and finish missing publication work. |

## Exact final validation commands

Required local validation:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy mvp cli
python -m pytest tests/test_mvp_*.py tests/mvp/ -q
python -m build
```

Required clean installed-wheel validation:

```bash
python -m venv /tmp/slugger-wheel-cert
. /tmp/slugger-wheel-cert/bin/activate
python -m pip install --upgrade pip
pip install dist/*.whl
slugger mvp build --help
```

Required protected credential validation:

```bash
codex --version
gh --version
git --version
slugger mvp build "Create a CLI task tracker with add, list, and done commands" --name task-tracker --repo OWNER/EMPTY-SANDBOX --base main
slugger mvp publish <run-id>
slugger mvp resume <run-id>
```

## Required GitHub sandbox assertions

Before closing issue #24, record one protected run proving:

- Branch creation.
- Commit creation and SHA.
- Push to the sandbox repository.
- One draft pull request with draft status true.
- PR body contains original idea, project name, template, Codex session ID, prompt version/hash, generated inventory, inventory hash, install/test/smoke results, known limitations, and Slugger run ID.
- Commit contains only generated inventory files.
- No `.venv`, `.pytest_cache`, databases, logs, or runtime state are committed.
- Second execution returns the same PR.
- Restarted publication returns the same PR.
- No automatic approval, merge, or release publication occurred.

## Known limitations

- MVP publication intentionally rejects non-empty repositories unless they are Slugger-managed for the same run.
- Real Codex and real GitHub sandbox evidence are credential-dependent and must run from protected CI or an administrator workstation.
- Branch protection and approval requirements may require repository administrator configuration outside the codebase.

## Real Codex CLI demo verification controls

Slugger now includes a manually triggered real-Codex demo workflow definition and local verification command. The implementation has unit coverage for deterministic generated-project manifests and `slugger mvp verify-existing`; it does not claim that a real OpenAI service run has occurred in this repository checkout.

Established by code and tests:
- `openai/codex-action@v1` is used only in the generation job of `.github/workflows/real-codex-cli-demo.yml`.
- The verification job is separate, depends on generation, checks out with persisted credentials disabled, verifies a JSON SHA-256 manifest before execution, and invokes `slugger mvp verify-existing`.
- The verifier delegates to the shared MVP `ProjectValidator` and `BasicRunner`, writes bounded JSON evidence, and detects protected-file mutation by comparing pre/post inventories of the approved artifact snapshot.
- Strict verification rejects custom PEP 517 build backends, in-tree backend paths, unsafe dependency references, nested `.git`, `.github`, generated symlinks, and package/runtime configuration files that could redirect execution.

A real Codex service execution requires a valid `OPENAI_API_KEY` GitHub Actions secret and a manual workflow dispatch in GitHub Actions.

## Baseline real-Codex run: 29460251536

The manual workflow run `29460251536` for `.github/workflows/real-codex-cli-demo.yml` at commit `a1c14bff01a0e81c67ab5bd5fb613a1e6cec4918` is recorded as durable sanitized evidence under `docs/certification/runs/29460251536/`.

That baseline run proved:

- Real Codex invocation through the GitHub Actions workflow.
- Generated project creation for `codex-cli-demo` / `codex_cli_demo`.
- Generated artifact upload.
- Deterministic manifest verification.
- Normal editable package installation.
- Three passing generated tests.
- Successful CLI smoke execution.
- Separate credential-free verification job.
- Machine-readable verification evidence upload.

That baseline run did **not** prove:

- OS-level sandboxing.
- Disabled outbound networking during generated-code execution.
- Hermetic dependency installation.
- Correct mutation detection against the actual execution copy.
- Full production certification.

Current classification for that baseline remains:

- Functional MVP: Passed
- Security Hardening: Partial
- Production Certification: Not Yet Approved

## Future certification record process

After a successful manual workflow dispatch, download the `verification-evidence-*` and `generated-demo-*` artifacts, then create a sanitized durable record with:

```bash
python scripts/create_certification_record.py \
  --run-id <workflow-run-id> \
  --evidence <path-to-verification-evidence.json> \
  --manifest <path-to-generated-project-manifest.json>
```

Review the generated files before committing. Do not commit API keys, GitHub tokens, authorization headers, raw process environments, unbounded logs, or the complete generated application unless repository policy explicitly changes.

## Action pin update process

All third-party actions in `.github/workflows/real-codex-cli-demo.yml` are pinned to immutable commit SHAs with release comments. To update an action, resolve the desired release tag to a commit SHA, review the upstream release notes and diff, update the `uses:` SHA plus the human-readable comment, run workflow tests and `actionlint`, and record the reviewed SHA in the next certification summary.

## v0.1.1 certification status note

Do not mark v0.1.1 certified until the required Python 3.11 and Python 3.13 CI jobs, golden MVP acceptance, package verification, and one protected manual user-idea publication run have passed. The protected run must demonstrate one generated branch, one draft PR, idempotent rerun behavior, uploaded publication evidence, triggered generated-PR checks, and no publication-token leakage in logs.
