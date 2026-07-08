<!--
  docs/DevelopmentStandards.md
  Purpose: Repository development standards, branching, PRs, CI, and testing guidance.
-->

# Development Standards

## Repository layout
- `src/` or `slugger/` — primary Python package and entrypoints
- `docs/` — project documentation (this directory)
- `tests/` — unit and integration tests
- `scripts/` — helper scripts for development and deployment

## Branching & workflow
- `main` is protected and represents the production-ready state.
- Feature branches: `feature/<name>`
- Bugfix branches: `fix/<name>`
- Release branches: `release/<version>`
- Hotfix branches: `hotfix/<version>`

## Commits & PRs
- Use Conventional Commits: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`.
- PRs must include: summary, motivation, testing instructions, and rollback notes if applicable.
- Require at least one approving review and passing CI before merge.

## Testing
- Write unit tests for core logic and agents orchestration.
- Integration tests should verify end-to-end job execution in a controlled environment.
- Run tests locally: `pytest` or the project's preferred test runner.

## CI / CD
- CI pipeline should run linters, formatters, static analysis, and tests on PRs.
- Fail build on lint/test failures to maintain quality.

## Tooling
- Python: use `black` for formatting and `flake8` for linting.
- Pre-commit hooks recommended to enforce formatting before commits.

## Code review checklist
- Tests added or updated for new behavior.
- No secrets or credentials in code changes.
- Clear docstrings and module-level documentation where applicable.
- No TODOs that block merging.

