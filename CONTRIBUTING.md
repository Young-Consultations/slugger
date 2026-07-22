# Contributing

Thank you for improving Slugger. Keep changes focused, reviewable, and aligned with the MVP architecture.

## Pull requests

- Use a focused branch and one logical change per pull request.
- Link the related issue when one exists.
- Include clear testing evidence and call out skipped checks.
- Document security, architecture, workflow, and generated-code impact.
- Do not commit secrets, generated credentials, private keys, or environment files.

## Slugger MVP contribution rules

- The focused MVP path is the supported execution path: user idea, constrained Codex generation, validation, isolated install/tests, restricted verification, and one draft pull request in the generated-output repository.
- Do not introduce a second MVP execution path.
- MVP code must preserve the existing architecture boundary between the CLI, `mvp/` services, integrations, and generated output.
- Workflow changes require security and least-privilege review.
- Generated code must never be automatically merged.
- New production behavior requires tests.
- Do not mix unrelated experimental AI-SDLC work into focused MVP pull requests.

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
python scripts/validate_repo_governance.py
```

## Generated projects

Generated projects are delivered through draft pull requests to `Young-Consultations/slugger-generated-demos`, require human review, and must include fresh-checkout install/test/run instructions. Do not automatically merge generated application pull requests.
