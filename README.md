# Slugger

Slugger is the execution and product-generation boundary in the Young Consultations
AI-assisted delivery system. The authoritative product direction is
[`docs/VISION.md`](docs/VISION.md); [`AI_CONTEXT.md`](AI_CONTEXT.md) defines the
required reading order and implementation policy.

## Current next-MVP status

The supported target interface is the organization next-MVP adapter described by
[`docs/next-mvp.md`](docs/next-mvp.md). It consumes
`ai-sdlc-contract/v2`, executes only an admitted task in this repository,
produces at most one validated managed draft pull request, and sends one canonical
result.

The issue #135 recovery work is no longer an unpublished candidate. The current
organization registry binds Slugger to immutable target
`codex-adapter-v2.3.2` at
`797f239579bf56fbd5d11d98a1a6b5bad36d98a8`, with passing
`TC-MVP-CI-001` evidence. Slugger is **disabled** in the current published
2.4.5 runtime state, and no Slugger REAL execution or Slugger-specific live
receiver acceptance is claimed. Current target activation is separate mutable
control-plane state enforced by the organization router.

The single `.github/workflows/codex-execute.yml` remains the canonical target
entry point; there is no parallel target adapter. Its exact 2.3.2 workflow/adapter
content and receiver pin are immutable target evidence and are not rewritten by
this documentation reconciliation. There is currently no supported local CLI,
manual Codex demo, publication, certification, release, or full-SDLC execution
path.

The organization source/control plane is currently published as
`ai-sdlc-v2.4.5`. Slugger's target-specific compatibility evidence remains:

```text
target adapter: codex-adapter-v2.3.2
target commit: 797f239579bf56fbd5d11d98a1a6b5bad36d98a8
shared compatibility source: Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a
contract: ai-sdlc-contract/v2
fixture manifest: TC-MVP-CI-001 v2.3.0 (29 scenarios)
```

Canonical schemas and fixtures remain owned by the organization control plane.
The byte-identical copies checked in here are offline validation inputs bound to
their upstream Git blob identities; they are not a local fork. See
[`docs/shared-contract-orchestration.md`](docs/shared-contract-orchestration.md)
for the subordinate integration summary and
`.ai-sdlc/conformance/tc-mvp-ci-001.json` for zero-effect evidence.

## Repository contents

Existing Python MVP, CLI, multi-agent, provider, publication, approval, release,
and full-SDLC modules and their tests are retained only as quarantined historical
or experimental blueprints. They are not installed as a console command, are not
called by the target workflow, and do not establish supported behavior or
next-MVP conformance. [`docs/mvp.md`](docs/mvp.md) is explicitly historical and
[`docs/production-readiness.md`](docs/production-readiness.md) is longer-term
background.

The repository-wide disposition and migration record is
[`docs/next-mvp-migration.md`](docs/next-mvp-migration.md).

## Development checks

Normal CI is hermetic: it has read-only repository permission and does not call
Codex or mutate GitHub branches or pull requests. Blueprint regression tests remain
to detect accidental code decay while extraction/removal decisions are deferred;
they are not next-MVP acceptance or certification evidence.

```bash
pip install -c constraints-ci.txt -e ".[test]"
ruff check .
ruff format --check .
python -m mypy mvp cli
pytest tests/
python -m build
git diff --check
```

## Responsibility boundary

Slugger does not own portfolio intent, priority, or approval; organization
contracts, routing, registration, compatibility, or result receiving; human
review or merge; release, deployment, or production decisions; or sibling
repository implementation. Automation will end at a draft pull request and a
canonical result. Local implementation and conformance do not enable the target;
activation remains an organization control-plane decision.

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and
[`docs/mvp-merge-governance.md`](docs/mvp-merge-governance.md) before contributing.
