<!--
  docs/DevelopmentStandards.md
  Purpose: developer workflow, branching model, CI/CD and testing standards.
-->

# Development Standards

## Repository layout
- `cmd/` or `src/` — application entrypoints
- `pkg/` — reusable libraries/packages
- `internal/` — package code not for external consumption
- `docs/` — design and process documentation
- `tests/` — integration and end-to-end tests
- `scripts/` — developer tooling and automation

## Branching & workflow
- `main` is the protected production branch.
- Feature branches use the `feature/<name>` prefix.
- Bugfix branches use the `fix/<name>` prefix.
- Release branches use `release/<version>`.
- Hotfix branches use `hotfix/<version>` and are merged into `main` and long-lived release branches.

## Pull requests
- PRs must target `main` from a feature branch.
- PR description must include: summary, motivation, testing steps, and rollback plan.
- At least one approving review required before merge.
- CI checks (lint, tests, build) must pass before merging.

## Commits
- Follow Conventional Commits: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
- Example: `feat(api): add batch slug generation endpoint`
- Keep atomic commits and write descriptive commit messages.

## Testing
- Unit tests for all new logic. Aim for fast, deterministic tests.
- Integration tests for public APIs and persistence.
- Use table-driven tests where applicable.
- Run tests locally before pushing: e.g., `go test ./...`, `pytest`, or `npm test` depending on language.

## CI / CD
- CI must run linting, static analysis, unit tests, and build steps.
- Enforce branch protection rules on `main`.
- Deployments automated via CD with manual approvals for production.

## Code review checklist
- Tests added for new behavior.
- No secrets in code or config.
- Functions and modules have clear documentation.
- No blocking TODOs or commented-out code.

## Tooling
- Add pre-commit hooks for formatting (gofmt, prettier, black) and basic checks.
- Use dependency management and pin versions where supported.

## Security
- Scan dependencies regularly (Dependabot or equiv.).
- Enforce least-privilege for service identities and secrets.

