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
and sends one canonical result. The issue #135 recovery implementation is now
registry-bound as immutable target `codex-adapter-v2.3.2` at
`797f239579bf56fbd5d11d98a1a6b5bad36d98a8` with passing local
shared-oracle evidence. Slugger remains disabled in the published organization
2.4.5 runtime state, and no Slugger REAL/live-receiver acceptance is claimed.

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

## Implementation authority and convergence policy

This section governs every implementation task. The approved product
[vision](docs/VISION.md), [requirements baseline](docs/requirements/README.md),
[architecture and design](docs/architecture/README.md),
[ADRs](docs/architecture/ADR.md), and
[organization next-MVP baseline](docs/next-mvp.md) are authoritative. Their stated
status and the authority hierarchy above still apply; this policy does not promote
draft, historical, experimental, deferred, or externally blocked material.

- Existing source code, workflows, schemas, tests, fixtures, packages, prompts,
  examples, and release artifacts are implementation blueprints or evidence—not
  requirements or architectural authority. Reuse them only where they conform to
  the authoritative documentation.
- An implementation artifact may be modified, replaced, or deleted when it
  conflicts with authoritative documentation. Later scoped tasks should remove
  conflicting, duplicated, obsolete, and out-of-scope implementation rather than
  treating current behavior as a constraint. Git history, release records, and
  ADRs—not live compatibility code—preserve historical behavior and decisions.
- There is no current backward-compatibility requirement. Do not preserve
  deprecated execution paths, duplicate contracts, wrappers, aliases, shims,
  transitional structures, fallback interfaces, dual-schema validation, or
  obsolete workflow inputs unless an authoritative requirement explicitly requires
  them.
- Converge on **one supported MVP contract and one active implementation path for
  each responsibility**. For this repository, the documented contract shape is
  `ai-sdlc-contract/v2` plus the exact schema/fixture identities at recovery
  candidate
  `Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`
  recorded in the next-MVP baseline. It remains externally owned; checked-in
  byte-identical files are pinned validation inputs, not a local contract fork.
  Mutable target activation is separately owned and enforced by the organization
  router before dispatch. A version discriminator does not imply support for older
  versions.
- Do not treat historical user-generation, certification, release, experimental
  full-SDLC, or diagnostic paths as additional active organization execution paths.
  Their existence does not broaden the next-MVP responsibility or preserve an
  alternate contract.
- Do not infer behavior, schemas, compatibility, authority, availability, or
  readiness from a sibling repository. Cross-repository assumptions may come only
  from explicit, versioned interface or release documents present in this
  repository and must retain their documented external/unverified status.
- Do not invent missing requirements, architecture, fixtures, credentials,
  ownership, or external behavior. Fail closed when safe behavior is defined;
  otherwise report the missing external dependency as a blocker to the affected
  implementation or readiness claim.
- Keep MVP scope narrow. Automation stops at a validated managed draft PR or a
  no-change, rejection, or failure result. It performs no automatic merge,
  deployment, production operation, autonomous approval, or production-readiness
  determination or claim.
- Before every implementation task, load this `AI_CONTEXT.md` completely, then
  follow its ordered reading path, authority hierarchy, repository boundaries, and
  task-relevant validation instructions before proposing or changing code.
- Documentation-only work authorizes no runtime deletion, contract change,
  workflow change, or product implementation. Artifact disposition belongs to a
  separately scoped implementation task.

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

- Fail closed on missing/invalid authority, unknown contract semantics, unsafe or
  ambiguous state, incomplete evidence, and ownership
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
- Normal conformance CI must use the pinned executable oracle and fakes and perform
  no Codex network call or real GitHub branch/PR mutation. Passing local conformance
  does not activate Slugger; mutable activation remains organization-router state.

## Development and validation workflow

Keep changes focused and trace them to applicable requirement, acceptance,
architecture, and interface IDs. Add or update applicable tests and evidence when
implementation changes are authorized. Install the checked-in test toolchain with:

```bash
pip install -c constraints-ci.txt -e ".[test]"
```

Run the CI-configured checks below, and run additional local checks (for example,
`pytest tests/` and `git diff --check`) when a task's risk or removal policy
requires broader validation:

```bash
ruff check .
ruff format --check .
python -m mypy mvp cli
python -m pytest tests/test_mvp_*.py -q
python -m pytest tests/mvp/test_task_tracker_acceptance.py -q
python scripts/test_codex_execute_contract.py
python scripts/run_tc_mvp_ci_001.py
git diff --exit-code -- .ai-sdlc/conformance/tc-mvp-ci-001.json
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

- The issue #135 recovery implementation exposes one two-input dispatch adapter
  and passes all 29 canonical scenarios through the real adapter seam with
  prohibited effects trapped at zero. Review/merge, immutable target tagging, and
  organization registry tag/commit/report binding are complete under
  `codex-adapter-v2.3.2` at
  `797f239579bf56fbd5d11d98a1a6b5bad36d98a8`. Slugger is still disabled and
  has no Slugger-specific REAL/live-receiver acceptance or production-readiness
  claim.
- Immutable target capability and mutable operational activation are separate.
  Historical enabled state is not part of Slugger's compatibility pin; the router
  owns and enforces current activation before dispatch. Local implementation,
  registration, and conformance must not enable Slugger.
- Shared compatibility source
  `Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`
  supplies executable `TC-MVP-CI-001` inputs and expected results. The immutable
  registered 2.3.2 target adapter retains its exact receiver pin as target evidence.
  Slugger binds byte-identical shared blobs and its target files in
  `config/mvp-conformance-pin.json`; it must not redefine their semantics.
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

No local contract-design decision blocks Slugger's registered target capability.
Human review/merge, immutable adapter tagging, registry tag/commit/report binding,
and deterministic compatibility evidence are complete for
`codex-adapter-v2.3.2`. The remaining Slugger-specific operational gates are
deliberate target activation, current credential/preflight readiness for the
Slugger environment, and controlled Slugger live execution/receiver evidence.
Those gates are not satisfied by consulting-playbook's 2.4.5 REAL evidence.
Exact organization-owned schemas, statuses, fixture expectations, receiver
semantics, identity, ownership, and duplicate behavior remain authoritative at
the immutable pin and must be consumed rather than redefined.

## Maintenance rule

Update this file whenever an authoritative file moves, approval status changes,
ownership boundaries change, the current interface/contract policy changes, or a
recorded blocker is resolved. Recheck every local link and keep the ordered path
concise. Preserve historical behavior in Git history, release records, or ADRs—not
as multiple active policies or compatibility paths in this file.
