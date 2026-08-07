# AI Context and Implementation Policy

## Purpose and usage

This file is the ordered entry point and standing implementation policy for every
AI agent working in this repository. Read it completely **before proposing or
making any change**, then follow the linked sources applicable to the task. This
file indexes canonical sources and records how to use them; it does not duplicate
or replace their detailed requirements, decisions, or acceptance criteria.

Use only evidence available in this repository. A reference to an external
repository identifies a dependency or ownership boundary, not access to that
repository or proof of its current implementation or conformance.

## Authority hierarchy

Apply this order, from highest to lowest authority:

1. The approved [product vision](docs/VISION.md) defines direction, purpose,
   intended outcomes, scope, and boundaries.
2. The approved [requirements baseline](docs/requirements/README.md) defines
   required behavior, constraints, interfaces, and acceptance conditions. The
   [current next-MVP selection](docs/next-mvp.md) selects the exact requirements
   in the present organization slice.
3. Approved [architecture and design documentation](docs/architecture/README.md)
   and [ADRs](docs/architecture/ADR.md) define system structure, responsibility
   allocation, security boundaries, and architectural decisions.
4. Current organization and repository interface documentation defines
   cross-repository interactions and ownership boundaries.
5. Existing code, workflows, schemas, tests, fixtures, packages, examples,
   prompts, and all other implementation artifacts are blueprints and evidence
   only.

Existing operation or code presence never overrides a higher-authority source.
An artifact deliberately aligned with the authoritative documentation may serve
as its executable enforcement, but a later conflict must be reported and resolved;
the artifact must not silently redefine the requirement.

Preserve every source's stated status. Draft, proposed, historical, experimental,
superseded, longer-term, unapproved, or implementation-ready material does not
become approved or implemented merely because it is linked here. When
authoritative sources materially conflict or leave ownership undecided, stop the
affected decision, name the sources and identifiers, record the gap below, and
seek accountable resolution. Do not infer a resolution from existing code.

## Repository role and ownership

`Young-Consultations/slugger` owns the Slugger execution and product-generation
boundary. For the current organization next-MVP slice, it accepts one admitted
task, validates and executes it within this repository, produces at most one
validated Slugger-managed draft pull request for a qualifying implement request,
and sends one canonical result. This is planned responsibility; the target adapter
is not yet implemented, enabled, certified, or cross-repository conformant.

Within that slice Slugger owns local contract and policy enforcement, identity and
candidate correlation, repository-confined execution, Codex invocation after
authorization, candidate inventory and validation, required tests, sanitized
evidence, idempotent draft ownership, safe diagnostics, and canonical result
construction/delivery behavior.

Slugger does **not** own portfolio intent, priority, or approval; organization
schemas, vocabularies, registration, routing, compatibility, or result receiving;
another repository's governance; GitHub service behavior; Codex/provider behavior;
human review, merge, release, deployment, or production decisions; or generated
products' production operations. Locally documented external dependencies are the
portfolio authority, the organization `.github` control plane and its pinned
contract/fixture release, Codex, GitHub, the result receiver, credential authority,
and accountable human reviewers. Slugger consumes or validates attributed facts at
those interfaces without assuming sibling-repository access or implementation.

## Ordered reading path

Read in this order, going deeper where the proposed change touches the subject:

1. **Direction:** [Vision](docs/VISION.md) for product purpose, supported direction,
   non-goals, and human authority.
2. **Current slice:** [Organization next-MVP baseline](docs/next-mvp.md) for the
   exact included/deferred IDs, pinned single contract, target-adapter behavior,
   external blockers, and implementation status.
3. **Requirements:** [Requirements index](docs/requirements/README.md), then
   [repository context](docs/requirements/RepositoryContext.md),
   [project requirements](docs/requirements/ProjectRequirements.md),
   [SRS](docs/requirements/SoftwareRequirementsSpecification.md),
   [functional requirements](docs/requirements/FunctionalRequirements.md),
   [nonfunctional requirements](docs/requirements/NonFunctionalRequirements.md),
   and [business rules](docs/requirements/BusinessRules.md). Consult
   [requirements traceability](docs/requirements/RequirementsTraceability.md) for
   acceptance coverage and [assumptions/open questions](docs/requirements/Assumptions.md)
   before relying on an unresolved external fact.
4. **Interfaces:** Read the locally available interface relevant to the change:
   [organization control plane](docs/requirements/Interface-organization-github.md),
   [portfolio authority](docs/requirements/Interface-portfolio-tasks.md),
   [GitHub platform](docs/requirements/Interface-github-platform.md),
   [AI generation provider](docs/requirements/Interface-ai-generation-provider.md),
   [generated-project target](docs/requirements/Interface-slugger-generated-demos.md),
   or [future consulting knowledge](docs/requirements/Interface-consulting-playbook.md).
   [Shared-contract orchestration](docs/shared-contract-orchestration.md) is a
   concise current-slice integration summary subordinate to the next-MVP baseline.
5. **Architecture:** [Architecture index](docs/architecture/README.md),
   [software architecture](docs/architecture/SoftwareArchitecture.md),
   [ADRs](docs/architecture/ADR.md),
   [repository boundaries](docs/architecture/RepositoryBoundaries.md),
   [interface architecture](docs/architecture/InterfaceArchitecture.md), and the
   relevant component, data-flow, state, configuration, deployment, error-handling,
   or observability design linked by the index. Use
   [architecture traceability](docs/architecture/ArchitectureTraceability.md) to
   connect current IDs to decisions and planned evidence.
6. **Security and contribution policy:** [Security architecture](docs/architecture/SecurityArchitecture.md),
   [security policy](SECURITY.md), [contribution policy](CONTRIBUTING.md), and
   [MVP merge governance](docs/mvp-merge-governance.md).
7. **Status-only/background material:** [Historical v0.1.x MVP](docs/mvp.md) is
   historical, while [production readiness](docs/production-readiness.md) is
   longer-term material. Neither defines the current organization next-MVP or
   proves current capability. Use the root [README](README.md) for repository
   orientation only where it agrees with higher-authority sources.

## Implementation authority and compatibility policy

- This project is pre-production, has one current user, and currently has **no
  backward-compatibility requirement**.
- Existing implementation is a blueprint, not product authority. Reuse an artifact
  only when it conforms to the approved requirements and design.
- Later implementation tasks may modify, replace, or remove conflicting,
  duplicated, obsolete, or out-of-scope code, workflows, schemas, tests, fixtures,
  packages, and examples. Git history preserves removed implementation and is the
  recovery mechanism for historical behavior.
- The organization supports **exactly one active cross-repository contract and one
  current execution path**. For this repository, the locally documented current
  interface is the immutable organization release 2.2.0 pin and its single
  `ai-sdlc-contract/v2` payload shape described in the next-MVP baseline. Local
  interfaces must conform to that organization-owned contract; local summaries or
  schemas cannot replace it.
- Earlier contract shapes, compatibility adapters, legacy aliases, migration
  layers, dual-schema validation, obsolete workflow inputs, and fallback interfaces
  must not be preserved unless a future approved requirement explicitly requires
  them. A version or discriminator may identify the one current payload shape; its
  presence does not require support for earlier versions.
- Do not treat the historical user-generation, certification, release, experimental
  full-SDLC, or diagnostic paths as additional active organization execution paths.
- This documentation task authorizes no deletion, contract change, workflow change,
  or product implementation. Artifact disposition belongs to a later scoped task.

## MVP boundaries

The current organization next-MVP includes only **FR-INT-01, FR-INT-02,
FR-CAT-01, FR-RUN-01, FR-WS-01, FR-PRV-01, FR-ART-01, FR-VAL-01, FR-DEP-01,
FR-EXE-01, FR-TST-01, FR-SMK-01, FR-EVD-01, FR-PUB-01, FR-PUB-02, FR-IDM-01,
FR-ERR-01, FR-RES-01, and FR-CNF-01**. The normative descriptions and acceptance
conditions remain in the requirements and next-MVP baseline, not here.

Explicitly deferred IDs are **FR-SCP-01, FR-RUN-02, FR-PRM-01, FR-WS-02,
FR-REC-01, FR-GOV-01, FR-LCM-01, FR-LCM-02, and FR-EXT-01**. Multi-agent
orchestration, a full autonomous SDLC, cross-repository modification, automatic
merge, release, deployment, production operations, provider substitution, and rich
v3 approval provenance are not part of this slice. Code or documentation presence
does not promote them.

## Security and change boundaries

- Fail closed on missing/invalid authority, unknown contract semantics, disabled
  registration, unsafe or ambiguous state, incomplete evidence, and ownership
  uncertainty. Only router-admitted canonical `approved` work is authorized;
  labels, `queued`, provider output, or successful checks cannot grant approval.
- Keep implement changes and commands repository-confined. Treat Codex output and
  candidate content as untrusted; inventory and statically validate before
  execution, and execute only inside the documented controlled boundary.
- Separate caller authentication, Codex, validation, publication, and result
  delivery into least-privilege credential phases. Never pass publication/result
  credentials to Codex or candidate commands, and never put secrets in prompts,
  candidates, logs, diagnostics, evidence, command lines, commits, or PRs.
- Automation ends at one demonstrably owned open **draft** PR. It must not mark
  ready, approve, merge, release, deploy, or make production-readiness decisions.
- Preserve repository isolation, exact candidate/evidence binding, redaction,
  deterministic delivery identity, and human product/architecture/security/review
  authority. Pre-production status and a single user do not weaken these controls.
- Normal conformance CI must use fakes and perform no Codex network call or real
  GitHub branch/PR mutation. The disabled external registry and fail-closed receiver
  skeleton prohibit live routed success until their documented external gates pass.

## Development and validation workflow

Keep changes focused and trace them to applicable requirement, acceptance,
architecture, and interface IDs. Add or update applicable tests and evidence when
implementation changes are authorized. Install the checked-in test toolchain with:

```bash
pip install -c constraints-ci.txt -e ".[test]"
```

The checked-in CI defines these locally supported checks; run all applicable checks
and the full suite when a task's risk or removal policy requires it:

```bash
ruff check .
ruff format --check .
python -m mypy mvp cli
python -m pytest tests/test_mvp_*.py -q
python -m pytest tests/mvp/test_task_tracker_acceptance.py -q
python -m build
pytest tests/
git diff --check
```

For documentation-only changes, review the diff, validate every changed Markdown
link, run any applicable configured checks, and run `git diff --check`. Do not run
credentialed, real-Codex, publication, release, or deployment paths unless an
approved task expressly requires them and their protected boundary is available.

## Rules for future AI implementation tasks

Every later AI task must:

1. Read this file completely and identify the controlling vision, requirement and
   acceptance IDs, architecture/ADR decisions, interfaces, and security boundaries.
2. Evaluate existing artifacts as blueprints; do not equate passing/current code
   with approved behavior or infer scope from it.
3. Make focused changes, preserve required behavior, test the applicable positive
   and fail-closed cases, and report evidence and residual blockers.
4. Never silently change approved requirements, architecture, security boundaries,
   ownership, or the single active contract. Report material contradictions and
   obtain accountable resolution rather than choosing the existing implementation.

Before removing or replacing any artifact in a later authorized task, the agent
must:

1. Identify the active, obsolete, duplicated, or deferred behavior it supports.
2. Trace that behavior to applicable requirements, architecture, interface
   documentation, or ADRs.
3. Search for and address every reference and dependency.
4. Preserve behavior required by an active requirement.
5. Update affected tests and documentation consistently.
6. Verify that no orphaned imports, links, workflow references, schema references,
   fixtures, or package dependencies remain.
7. Run the full applicable validation suite.
8. Report every material removal or replacement and its reason.

Legacy-looking artifacts are not automatically deleted; determine each artifact's
disposition during the relevant implementation task.

## Known gaps or conflicts

- The current adapter is explicitly not implemented, enabled, or certified. The
  organization registry is disabled, and the pinned result receiver is a
  fail-closed skeleton. Live successful result delivery requires an externally
  owned implemented receiver, coordinated immutable repin/release, local evidence,
  and registry enablement.
- `TC-MVP-CI-001` does not locally provide executable inputs and expected outputs
  for every scenario. **FR-CNF-01** can be planned against its named coverage, but
  full shared-fixture conformance must not be claimed or fabricated.
- External contract files and sibling repositories are unavailable here. Their
  documented immutable pin is the alignment target, not locally verified evidence
  of their present state or Slugger conformance.
- [Repository context](docs/requirements/RepositoryContext.md) describes backward
  compatibility for declared windows as a general lifecycle responsibility, while
  the current pre-production policy establishes no backward-compatibility
  requirement and one active contract shape. No declared current compatibility
  window is identified locally; a future approved window would require this file
  and the implementation policy to be updated.
- [Historical MVP documentation](docs/mvp.md) and
  [longer-term production-readiness material](docs/production-readiness.md) describe
  other execution paths and implementation claims. Their own status notices keep
  them outside the authoritative current slice; they must not be used to claim the
  next-MVP adapter exists or to preserve multiple active paths.
- Open external/security/operational decisions **OQ-01 through OQ-16** remain in
  [assumptions and open questions](docs/requirements/Assumptions.md). Consult the
  owning record rather than copying that backlog here or manufacturing answers.

These gaps block the affected live/conformance claims but do not block local,
disabled, no-Codex implementation against the approved baseline.

## Maintenance rule

Update this file whenever an authoritative file moves, approval status changes,
ownership boundaries change, the current interface/contract policy changes, or a
recorded blocker is resolved. Recheck every local link and keep the ordered path
concise. Preserve historical behavior in Git history, release records, or ADRs—not
as multiple active policies or compatibility paths in this file.
