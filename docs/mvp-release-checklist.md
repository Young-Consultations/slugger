## Project status for v0.1.1

Current release target: **Slugger v0.1.1**. The canonical user-facing product path is **User idea → Codex generation → validation → isolated installation/tests → restricted verification → generated Git branch → idempotent draft pull request → evidence artifact**.

The user-facing GitHub Actions workflow is **User Idea Codex Slugger MVP Demo** (`.github/workflows/user-idea-codex-cli-demo.yml`). General **CI** is limited to deterministic tests, quality checks, packaging, and golden acceptance tests; it does not publish generated applications. **Canonical Real Codex Slugger MVP Demo** remains an internal, non-user-facing certification workflow for the fixed `hello-codex` scenario.

Required secrets and permissions: `OPENAI_API_KEY` is required only in the protected Codex generation environment. The final same-job publication step uses `SLUGGER_GITHUB_TOKEN` scoped only to the target repository with Contents read/write, Pull requests read/write, and Metadata read; non-publication jobs remain `contents: read`.

Expected outputs are a sanitized generated Python CLI project, a protected artifact manifest, restricted-verifier evidence, a deterministic `slugger/generated-<project>-<run>` branch, and one draft PR. Publication is skipped/blocked when generation, validation, installation, tests, restricted verification, manifest validation, or path-safety checks fail. Reruns reuse persisted run evidence, deterministic branch naming, and existing draft PR detection to avoid duplicate PRs.

Known limitations: v0.1.1 supports constrained dependency-minimal Python CLI projects; generated code still requires human review; real Codex/GitHub publication requires protected GitHub Actions credentials; broader AI-SDLC packages remain experimental candidates for later extraction in v0.2.0 or later.

# MVP Release Checklist

Use this checklist before tagging the first Slugger MVP release.

## v0.1.0 readiness

- [x] GitHub Actions workflow `Canonical Real Codex Slugger MVP Demo` completes successfully.
- [x] Real Codex generation job uses the protected `codex-demo` environment and `OPENAI_API_KEY` environment secret.
- [x] Generated CLI validation passes: packaging policy, dependency policy, required files, and source inventory checks.
- [x] Generated CLI tests pass under the verifier virtual environment.
- [x] Non-interactive smoke test passes with `python -m hello_codex.main greet Joseph` and stdout exactly `Hello, Joseph!`.
- [x] Success artifact `slugger-mvp-cli-demo-<run_id>` is uploaded and downloaded manually.
- [x] Downloaded artifact is manually tested locally with the commands in `MVP_ARTIFACT_README.md`.
- [x] Documentation names all required secrets and variables without real secret values.
- [x] Known limitations below are reviewed and accepted.
- [x] Version is selected as `v0.1.0` unless the repository versioning scheme changes.
- [x] Release tag is ready to create after manual artifact verification.

## Known limitations

- The supported MVP release path is the manual GitHub Actions workflow only; local Codex runs remain developer diagnostics.
- The generated demo is intentionally constrained to a dependency-minimal Python CLI named `hello-codex`.
- General CI does not publish generated code. The user-idea workflow publishes only after all MVP gates pass and only to an empty or Slugger-managed sandbox target repository.
- Real Codex output is non-deterministic; the verifier rejects outputs that do not satisfy the documented contract.
- Container verification requires Docker availability on the GitHub-hosted runner.

## Deferred post-MVP work

- Add a versioned release asset publishing workflow after the manual MVP path is proven.
- Support additional generated project templates beyond the `hello-codex` CLI.
- Add optional organization-specific policy packs for stricter artifact review.
- Add scheduled compatibility checks for newer Python and action versions.

## Release certification record

- Release version: `v0.1.0`
- Certification workflow run: `29601077462`
- Certified branch: `main`
- Certified commit: `685ae1b63313f3401d8876f9210f09c21186b7f0`
- Success artifact: `slugger-mvp-cli-demo-29601077462`
- Certification artifact: `slugger-codex-certification-29601077462`
- Manual release steps: completed and attested by the repository owner
- Release decision: approved
- Verification date: 2026-07-18

### Automated checks (release branch)

- `ruff check .` — passed
- `ruff format --check .` — passed
- `python -m mypy mvp cli` — passed (no issues found in 18 source files)
- `python -m compileall .` — passed
- `python -m build` — passed (slugger-0.1.0.tar.gz and slugger-0.1.0-py3-none-any.whl)
- `python -m pytest -q` — 847 passed, 1 skipped; 6 environment-specific failures in sandbox (pip install unavailable in restricted runner); all checks pass in certified workflow run `29601077462`

### Post-certified-commit changes

Commits `f74ed2f` and `e481f81` (merged after certified commit `685ae1b`) add consulting operating system templates — documentation only, no product code changes. Release continues as approved.

## v0.1.1 release checks to keep open

- Confirm `constraints-ci.txt`, `mvp/basic_runner.py`, and `docker/mvp-verifier.Dockerfile` agree on verifier tool versions through the automated consistency test.
- Confirm the user-idea success artifact contains only the generated demo, manifest, generation summary, verification evidence, publication summary, and artifact README.
- Confirm same-job publication works without transferring a complete `SLUGGER_HOME` between jobs.
- Confirm `SLUGGER_GITHUB_TOKEN` has only target-repository Contents read/write, Pull requests read/write, and Metadata read permissions.
