# Changelog

## Slugger v0.1.2 - 2026-07-20

### Changed

- Completed issue #63 by documenting deterministic publication identity for generated draft PRs. Publication identity is independent of GitHub workflow run IDs and Slugger run IDs, and repeated logical requests reuse one Slugger-managed draft PR instead of creating one PR per run.
- Documented safe existing-draft updates: Slugger validates machine-readable ownership markers, repository, base branch, project, template, prompt hash, publication identity, and draft state before reusing a PR.
- Documented safe migration of legacy run-ID branches when exactly one matching Slugger-owned draft PR is found, including `--force-with-lease` branch updates and PR metadata refresh.
- Documented duplicate-state recovery and race handling: multiple matching drafts fail safely without creating another PR, and create races are recovered by re-querying for a valid matching draft.
- Documented stale generated-file cleanup for files previously recorded in Slugger inventory while protecting unrelated repository files.

### Release evidence

- Certified GitHub Actions run: `29717362202`
- Certified source branch: `main`
- Certified source commit: `59a4142979a24a10ff697730c8ef49ec6c2030ee`
- Slugger run ID: `20f3c537bcf6480a9080d457f9414616`
- Manifest digest: `df3decd17b1ca9df01bb5e6cf41c2f82d1a5815ce0fd3b9dc0dac24e94b69daa`
- Certification artifact: `slugger-user-idea-codex-certification-29717362202`
- Certification artifact digest: `sha256:33c201af38a00d8058ea8e048cbf7dbbdc7b93468e48fb8049e230cbc237f231`
- Verifier diagnostics: `verifier-diagnostics-29717362202`
- Success artifact: `slugger-user-idea-cli-demo-29717362202`
- Updated existing draft PR: `mightyjoe909/slugger-generated-demos#2`

### Known limitations

- Slugger still publishes only after same-job manifest validation, restricted verification, token-isolated target validation, and path-safety gates pass.
- Ambiguous duplicate Slugger draft PRs require manual operator recovery; production code does not automatically close duplicate or user-owned PRs.
- Generated projects remain constrained Python CLI drafts that require human review before production use.
