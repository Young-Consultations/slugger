# Contributing

Thank you for improving Slugger. Keep changes focused, reviewable, and aligned with the MVP architecture.

## Pull requests

- Use a focused branch and one logical change per pull request.
- Link the related issue when one exists.
- Include clear testing evidence and call out skipped checks.
- Document security, architecture, workflow, and generated-code impact.
- Do not commit secrets, generated credentials, private keys, or environment files.


## Organization-routed AI-SDLC execution

Production Codex tasks for Slugger now originate in `Young-Consultations/portfolio-tasks`, where intake metadata and explicit approval are owned. Routing and canonical validation are owned by the organization control plane in `Young-Consultations/.github`. Slugger is a registered target executor only, through `.github/workflows/codex-execute.yml`.

Slugger does not authorize production execution from local issue labels; `codex-ready` is no longer a production trigger. The supported contract is `ai-sdlc-contract/v2`, pinned to the organization control-plane release `ai-sdlc-v2.1.0`. Automated publication remains draft-only and requires human review before any merge.

## Slugger MVP contribution rules

- Production AI-SDLC execution is organization-routed: portfolio-tasks owns intake and approval, Young-Consultations/.github owns routing and canonical validation, and Slugger owns target execution, validation, and draft-only publication.
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
```

## Generated projects

Generated projects are delivered through draft pull requests to `Young-Consultations/slugger-generated-demos`, require human review, and must include fresh-checkout install/test/run instructions. Do not automatically merge generated application pull requests.
