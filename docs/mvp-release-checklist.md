# MVP Release Checklist

Use this checklist before tagging the first Slugger MVP release.

## v0.1.0 readiness

- [ ] GitHub Actions workflow `Canonical Real Codex Slugger MVP Demo` completes successfully.
- [ ] Real Codex generation job uses the protected `codex-demo` environment and `OPENAI_API_KEY` environment secret.
- [ ] Generated CLI validation passes: packaging policy, dependency policy, required files, and source inventory checks.
- [ ] Generated CLI tests pass under the verifier virtual environment.
- [ ] Non-interactive smoke test passes with `python -m hello_codex.main greet Joseph` and stdout exactly `Hello, Joseph!`.
- [ ] Success artifact `slugger-mvp-cli-demo-<run_id>` is uploaded and downloaded manually.
- [ ] Downloaded artifact is manually tested locally with the commands in `MVP_ARTIFACT_README.md`.
- [ ] Documentation names all required secrets and variables without real secret values.
- [ ] Known limitations below are reviewed and accepted.
- [ ] Version is selected as `v0.1.0` unless the repository versioning scheme changes.
- [ ] Release tag is ready to create after manual artifact verification.

## Known limitations

- The supported MVP release path is the manual GitHub Actions workflow only; local Codex runs remain developer diagnostics.
- The generated demo is intentionally constrained to a dependency-minimal Python CLI named `hello-codex`.
- The workflow does not publish generated code to another repository or open a generated-code pull request.
- Real Codex output is non-deterministic; the verifier rejects outputs that do not satisfy the documented contract.
- Container verification requires Docker availability on the GitHub-hosted runner.

## Deferred post-MVP work

- Add a versioned release asset publishing workflow after the manual MVP path is proven.
- Support additional generated project templates beyond the `hello-codex` CLI.
- Add optional organization-specific policy packs for stricter artifact review.
- Add scheduled compatibility checks for newer Python and action versions.
