# Contributing

Thank you for improving Slugger. Keep changes focused, reviewable, and aligned with the MVP architecture.

## Pull requests

- Use a focused branch and one logical change per pull request.
- Link the related issue when one exists.
- Include clear testing evidence and call out skipped checks.
- Do not commit secrets, generated credentials, private keys, or environment files.

## Required tests

Run the relevant subset for your change and prefer the full MVP validation before review:

```bash
python -m compileall mvp cli
python -m ruff check .
python -m ruff format --check .
python -m mypy mvp cli
python -m pytest -q
python -m build
python scripts/check_obsolete_namespace.py
```

## Architecture boundaries

Slugger's MVP path remains: user idea, constrained Codex generation, validation, isolated install/tests, restricted verification, and one draft pull request in the generated-output repository. Do not introduce a second MVP execution path, a new workflow engine, or unrelated issue-automation parsers.

## Workflow and security review

GitHub Actions changes must use least-privilege permissions, avoid credential exposure, keep external actions pinned to immutable SHAs when touched, and preserve protected environment boundaries for Codex and publication tokens.

## Generated projects

Generated projects are delivered through draft pull requests, require human review, and must include fresh-checkout install/test/run instructions. Do not automatically merge generated application pull requests.
