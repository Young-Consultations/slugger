## Project status for v0.1.2

Current release target: **Slugger v0.1.2**. The canonical user-facing product path is **User idea → Codex generation → validation → isolated installation/tests → restricted verification → generated Git branch → idempotent draft pull request → evidence artifact**.

The user-facing GitHub Actions workflow is **User Idea Codex Slugger MVP Demo** (`.github/workflows/user-idea-codex-cli-demo.yml`). General **CI** is limited to deterministic tests, quality checks, packaging, and golden acceptance tests; it does not publish generated applications. **Canonical Real Codex Slugger MVP Demo** remains an internal, non-user-facing certification workflow for the fixed `hello-codex` scenario.

Required secrets and permissions: `OPENAI_API_KEY` is required only in the protected Codex generation environment. Target validation and the final same-job publication step use `SLUGGER_GITHUB_TOKEN` scoped only to the target repository with Contents read/write, Pull requests read/write, and Metadata read; non-publication jobs remain `contents: read`.

Expected outputs are a sanitized generated Python CLI project, a protected artifact manifest, restricted-verifier evidence, a deterministic `slugger/generated-<project>-<stable-identity-prefix>` branch, and at most one Slugger-managed draft PR per logical request. Publication is skipped/blocked when generation, validation, installation, tests, restricted verification, manifest validation, or path-safety checks fail. Reruns use a stable publication identity independent of workflow and Slugger run IDs, validate machine-readable PR ownership markers, safely migrate a matching legacy run-ID draft PR, update the existing branch/PR with latest verified output, remove stale Slugger-owned generated files, recover safely from create races, and fail closed when duplicate matching drafts or mismatched PR markers are detected.

Known limitations: v0.1.2 supports constrained dependency-minimal Python CLI projects; generated code still requires human review; real Codex/GitHub publication requires protected GitHub Actions credentials; broader AI-SDLC packages remain experimental candidates for later extraction in v0.2.0 or later.

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

## v0.1.2 release checks

- [x] Issue #63 implementation is merged on `main` and preserves manifest verification, restricted verification, token isolation, inventory/path safety, target-repository policy, and same-job publication boundaries.
- [x] Publication identity is deterministic across workflow and Slugger run IDs and uses the stable branch form `slugger/generated-<project>-<stable-identity-prefix>`.
- [x] Repeated logical requests validate machine-readable Slugger ownership markers and update one matching draft PR instead of creating one PR per run.
- [x] Legacy run-ID draft branches can be discovered and safely updated when exactly one matching Slugger-owned draft PR exists.
- [x] Duplicate matching drafts, non-draft PRs, closed PRs, merged PRs, foreign PRs, wrong-base PRs, and marker-mismatched PRs are not silently reused.
- [x] Stale Slugger-owned generated files are removed from prior inventories while unrelated files are protected.
- [x] Concurrent PR creation is race-safe through re-query and validated reuse.
- [x] Diagnostics and `publication-summary.json` report discovery, reuse/update behavior, duplicate detection, branch updates, PR updates, and race recovery.
- [x] Release automation verifies this checklist, package version `0.1.2`, CI/release checks, build artifacts, annotated tag safety, and idempotent GitHub Release creation before publishing.

## v0.1.2 certification record

- Release version: `v0.1.2`
- Certification workflow run: `29717362202`
- Certified branch: `main`
- Certified commit: `59a4142979a24a10ff697730c8ef49ec6c2030ee`
- Slugger run ID: `20f3c537bcf6480a9080d457f9414616`
- Manifest digest: `df3decd17b1ca9df01bb5e6cf41c2f82d1a5815ce0fd3b9dc0dac24e94b69daa`
- Certification artifact: `slugger-user-idea-codex-certification-29717362202`
- Certification artifact digest: `sha256:33c201af38a00d8058ea8e048cbf7dbbdc7b93468e48fb8049e230cbc237f231`
- Verifier diagnostics: `verifier-diagnostics-29717362202`
- Success artifact: `slugger-user-idea-cli-demo-29717362202`
- Updated existing draft PR: `mightyjoe909/slugger-generated-demos#2`
- Release decision: approved after this release PR merges to `main` and required checks pass.
