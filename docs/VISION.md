# Slugger Product Vision

This document is the authoritative statement of organization context and product intent for Slugger. It defines direction and boundaries; it does not assert that future capabilities are implemented, and it is not a requirements specification. For current operating instructions, use the repository [README](../README.md) and [MVP guide](mvp.md).

## Organization Vision

Young Consultations is building a governed AI-assisted software development operating system that turns human intent into approved, traceable, and reviewable software delivery. GitHub serves as the system of record for portfolio decisions, engineering work, execution evidence, and human approval. Specialized repositories collaborate through explicit versioned contracts so that planning, governance, AI execution, product generation, and consulting knowledge can evolve independently without sacrificing safety, accountability, or architectural coherence.

The operating system is intended to increase the leverage of a software leader, consultant, or small engineering team and to support, rather than bypass, the professional software development lifecycle (SDLC). AI execution remains bounded, reviewable, and subordinate to human authority. Each repository has a specific responsibility, and cross-repository coordination uses versioned contracts carrying complete task context. Expansion is incremental, validated, and governed.

## Slugger’s Role in the Organization

Slugger owns the **AI Software Factory product** within a larger organization whose responsibilities are deliberately separated. The following relationship descriptions are authoritative context supplied for this vision; they are not findings from inspection of the other repositories:

| Repository | Responsibility |
| --- | --- |
| `Young-Consultations/.github` | Organization contracts, routing, registration, compatibility, and control-plane verification. |
| `Young-Consultations/portfolio-tasks` | Structured work intake, portfolio governance, prioritization, and explicit execution approval. |
| `Young-Consultations/slugger` | The AI Software Factory product. |
| `Young-Consultations/consulting-playbook` | Reusable consulting methods, assessments, and delivery playbooks. |

Slugger consumes complete, approved work context through explicit versioned contracts; it does not take ownership of organization routing, canonical contracts, portfolio priority, or execution approval. GitHub is the system of record joining portfolio decisions, engineering work, execution evidence, and human approval without collapsing repository responsibilities.

## Product Vision

Slugger is a governed AI Software Factory that transforms an approved software idea into a validated, traceable, and reviewable software project while applying professional engineering practices throughout the delivery lifecycle. Slugger is intended to multiply the capability of a software leader or small engineering team, not replace human product judgment, architectural accountability, security responsibility, or code review.

This vision governs product direction. The supported MVP is a deliberately narrow proving path, while the repository's broader multi-agent and full-SDLC components are experimental inputs to future design—not evidence that the long-term product already exists.

## Problem Statement

Software ideas often lose fidelity and traceability as they move between planning, architecture, implementation, testing, and release. AI can accelerate individual steps, but uncontrolled generation can increase inconsistency, security risk, rework, and uncertainty. Slugger addresses this by placing AI generation inside a governed engineering process that produces reviewable software and evidence.

## Product Purpose

Slugger exists to reduce the effort required to move from a well-defined software intent to working, reviewable software while preserving the artifacts, validation, decisions, and evidence expected from a professional engineering process.

The value is not generation alone. It is a controlled path in which users can understand the input, inspect the output, evaluate verified evidence, and retain authority over consequential decisions.

## Primary Users

The primary target users are:

* software engineering leads;
* software program managers;
* technical consultants;
* architects;
* small engineering teams; and
* technically capable product owners.

Generated applications may serve many kinds of end users, but “any user” is not an adequate primary product persona for Slugger itself. Requirements development should refine the needs and operating contexts of the identified professional users rather than substitute personas of generated applications.

## User Outcomes

Users should be able to:

* turn a bounded idea into a working project more quickly;
* understand what Slugger generated and why;
* receive validation and test evidence with the output;
* reproduce or safely retry a run;
* review changes through GitHub;
* retain control over architectural and release decisions; and
* progressively use more SDLC capabilities without losing governance.

These are intended product outcomes, not claims that every outcome is complete in the current implementation.

## Near-Term Product Vision

The immediate product focus is a dependable, constrained idea-to-runnable-project path:

```text
Approved and bounded software idea
→ isolated generation workspace
→ controlled Codex generation
→ structural and policy validation
→ isolated installation
→ automated tests
→ deterministic smoke verification
→ evidence and manifest creation
→ draft GitHub pull request
→ human review
```

Near-term reliability is more important than broad autonomous capability. The supported direction is dependency-minimal Python CLI generation, with publication prevented unless the applicable validation and verification gates pass.

## Long-Term Product Vision

Over time, Slugger should support a governed end-to-end software lifecycle:

```text
Vision
→ requirements
→ analysis
→ architecture
→ UX and interface design
→ data and API design
→ implementation
→ testing
→ security review
→ documentation
→ CI/CD
→ release
→ deployment
→ maintenance and learning
```

The long-term lifecycle must be composed of bounded capabilities with explicit inputs, outputs, review points, and evidence. It must not be implemented as an unrestricted autonomous agent. The sequence is a direction for staged requirements and architecture work, not a statement of current availability.

### Current and long-term direction

| Area | Current supported direction | Long-term direction |
| --- | --- | --- |
| Input | Bounded small-project idea | Approved lifecycle intent and requirements |
| Output | Constrained validated project | Complete traceable software-system artifacts |
| Lifecycle coverage | Generation, validation, tests, smoke check, draft PR | Governed end-to-end SDLC |
| Application scope | Dependency-minimal Python CLI projects | Additional project and application classes |
| Agent model | Narrow orchestration around controlled generation | Specialized bounded lifecycle capabilities |
| Human role | Approval, review, merge, production decision | Same authority retained across all phases |

## Supported MVP Boundary

The supported MVP direction accepts a bounded idea for a small, dependency-minimal Python CLI project. It keeps generated files in a run-specific workspace separate from Slugger's source, constructs a constrained and versioned prompt, invokes Codex in the generation boundary, inventories and validates the result, installs and tests it in isolation, performs a deterministic CLI smoke check, retains structured state and evidence, and publishes verified output through a draft pull request. Repository workflows distinguish the user-facing generation path from the fixed certification path and general CI.

The boundary is intentionally fail-closed: unsafe paths, prohibited or malformed output, failed installation, failed tests, failed smoke verification, integrity or manifest failure, and ambiguous publication ownership prevent publication. Publication identity and retained run state support controlled retry and avoidance of uncontrolled duplicate draft pull requests. A passing check establishes only the evidence that check actually produced; it does not make the generated project production-ready.

The operational details and known limitations remain in [the MVP guide](mvp.md). This vision does not broaden the MVP beyond the `cli` template or dependency-minimal Python CLI projects, and it does not turn certification or local diagnostic paths into additional product classes.

## Experimental System Boundary

The repository also contains a broader multi-agent AI-SDLC implementation, including planning agents, shared lifecycle artifacts, workflow recipes and orchestration, providers, design integrations, and later-lifecycle concepts. Those components are experimental research material. They do not define supported MVP behavior, are not prerequisites for the MVP path, and must not be represented as a currently available governed end-to-end lifecycle.

In particular, the experimental product-vision, requirements, and user-story agents generate project artifacts inside the experimental workflow; they are not the authors or maintainers of this authoritative Slugger product vision. Their existence does not mean requirements development, architecture, deployment, or other long-term phases are supported. Promotion of any experimental capability requires a proven boundary, explicit contracts, validation, evidence, human review points, and integration without violating the MVP architecture boundary.

## Product Principles

* Begin with a bounded and reviewable intent.
* Keep generated work isolated from Slugger’s own source tree.
* Validate before installation.
* Install and test in an isolated environment.
* Publish only verified work.
* Use draft pull requests as the automation boundary.
* Preserve prompts, manifests, test results, and decision evidence.
* Fail closed on ambiguity, unsafe paths, invalid output, or incomplete verification.
* Keep the supported MVP path separate from experimental full-SDLC code.
* Expand lifecycle coverage only after the narrower path is reliable.
* Keep humans responsible for approval, architecture, review, merge, and production use.

## Explicit Non-Goals

Slugger is not intended to:

* autonomously decide business priorities;
* approve its own work;
* silently modify production repositories;
* merge its own pull requests;
* replace a product owner, architect, security authority, or reviewer;
* claim generated code is production-ready merely because it compiles or passes limited tests;
* centralize organization-wide portfolio governance;
* own the organization router or canonical cross-repository contracts; or
* support every application type in the initial product release.

## Measures of Vision Success

At the product-outcome level, the vision is succeeding when:

* generated projects are understandable, runnable, and reviewable;
* every supported run has traceable inputs, outputs, evidence, and status;
* validation failures prevent publication;
* reruns behave deterministically and do not create uncontrolled duplicate work;
* the supported MVP path remains architecturally isolated from experimental systems;
* users can distinguish verified evidence from unverified AI claims;
* expansion into additional SDLC phases preserves explicit review boundaries; and
* the product can consume approved organization work without taking ownership of portfolio approval.

Requirements development should turn these outcomes into measurable verification criteria without treating them as proof of current implementation completeness.

## Constraints and Guardrails

* **Human authority:** Humans retain responsibility for intent approval, product and architecture judgment, security decisions, review, merge, release, deployment, and production use.
* **Repository responsibility:** Slugger remains an execution and product-generation system; portfolio governance, organization routing, and canonical cross-repository contracts remain outside its ownership.
* **Complete contracted context:** Cross-repository execution depends on explicit, versioned contracts and complete approved task context, rather than implicit assumptions or local labels.
* **Isolation:** Generation must not use Slugger's source tree as the generated-project workspace, and installation or execution of generated output occurs only in controlled isolation.
* **Evidence before claims:** Status, manifests, prompts, checks, and decision evidence distinguish observed verification from provider assertions.
* **Fail-closed publication:** Ambiguous identity, unsafe output, incomplete evidence, or a failed required gate blocks automated publication.
* **Draft-only automation boundary:** Automation may prepare a reviewable draft pull request but does not approve, merge, or promote its own work.
* **Secrets and least privilege:** Providers and publication integrations receive only the credentials and permissions required for their bounded phase; generated code does not receive publication authority.
* **Current project-class limit:** The initial supported application class remains a constrained, dependency-minimal Python CLI.
* **No production-readiness shortcut:** Compilation, narrow validation, tests, or smoke checks do not replace threat analysis, security review, operational readiness, or accountable production decisions.

## Evolution Strategy

Evolution starts by making the near-term path dependable, observable, safe to retry, and clear about the evidence it provides. Gaps discovered in the current path take precedence over breadth. New project classes or lifecycle phases are introduced one bounded capability at a time, with explicit versioned inputs and outputs, isolated execution where needed, validation and failure behavior, retained evidence, compatibility expectations, and a named human review point.

Experimental components remain separated until their boundaries are demonstrated through requirements, architecture decisions, and verification. Provider-specific behavior stays behind replaceable integration boundaries. Each increment is evaluated against the product principles and success measures before becoming supported; a monolithic autonomous workflow is not the target architecture.

## Transition to Requirements Development

The next lifecycle phase derives—not invents—requirements through this model:

```text
Product vision
→ user outcomes
→ product capabilities
→ product constraints
→ functional requirements
→ non-functional requirements
→ lifecycle interface requirements
→ evidence and artifact requirements
→ verification criteria
→ product backlog
```

This document stops at capability scope. The next phase should address the following groups without allowing the experimental implementation to predetermine the requirements:

| Capability group | Scope for requirements development |
| --- | --- |
| Idea and intent intake | Define how approved software intent and its complete originating context enter Slugger and remain traceable. |
| Scope bounding | Define how Slugger identifies, communicates, and enforces the limits of an accepted generation or lifecycle run. |
| Project templates and supported project classes | Define the governed catalog of project shapes Slugger can generate and the criteria for adding a class. |
| Prompt construction and versioning | Define how bounded intent becomes a reproducible provider prompt with identifiable versions and retained provenance. |
| Codex provider integration | Define the controlled Codex execution boundary, result capture, failure semantics, and separation from product orchestration. |
| Isolated workspace management | Define creation, containment, lifecycle, inspection, and cleanup of run-specific generated-work locations. |
| Generated-file policy | Define permitted paths, file types, contents, inventories, mutation rules, and source-tree protections for generated output. |
| Dependency management | Define allowable dependencies, resolution controls, provenance, and behavior when dependencies cannot be safely obtained. |
| Validation | Define pre-execution structural, syntax, packaging, integrity, and policy checks and their evidence. |
| Installation isolation | Define the controlled environment in which generated software is installed without contaminating Slugger or a production system. |
| Automated testing | Define how generated-project tests are selected, bounded, executed, recorded, and interpreted. |
| Deterministic smoke verification | Define stable executable checks that establish the generated project's minimum promised behavior. |
| Evidence and manifest generation | Define the review evidence, inventories, digests, provenance, and verified-versus-claimed status retained for each run. |
| Run-state persistence | Define durable run identity, phase state, results, errors, evidence references, and status history. |
| Retry, resume, and idempotency | Define safe continuation and replay behavior that avoids repeated generation or uncontrolled duplicate publication. |
| GitHub publication | Define bounded transfer of verified output to deterministic branches and reviewable GitHub changes. |
| Draft-PR ownership | Define how Slugger identifies, updates, reuses, and refuses ambiguous draft pull requests it manages. |
| Human approval and review integration | Define the explicit approval inputs and review points that automation consumes without granting itself authority. |
| Security and secret handling | Define trust boundaries, least-privilege credentials, redaction, untrusted-output controls, and security decision ownership. |
| Observability and diagnostics | Define safe operational signals that explain run progress, provider activity, checks, failures, and correlation across boundaries. |
| Failure recovery | Define actionable, evidence-preserving recovery paths for every phase without bypassing required gates. |
| Lifecycle artifact management | Define identification, versioning, traceability, review state, retention, and handoff of professional SDLC artifacts. |
| Future requirements and architecture stages | Define how later planning and design phases become bounded capabilities with governed inputs, outputs, and review gates. |
| Extension and provider boundaries | Define replaceable provider and extension contracts that preserve product policy, compatibility, and evidence semantics. |

Detailed shall-statements, user stories, acceptance criteria, APIs, schemas, and implementation tasks are deliberately deferred to subsequent lifecycle work.

## Vision Assumptions Requiring Validation

| Assumption | Why it matters | How requirements development should validate it |
| --- | --- | --- |
| The initial supported customer values reliable constrained generation more than broad autonomy. | This determines whether reliability-first sequencing addresses the primary user's highest-value problem. | Interview representative primary users and rank constrained reliability, breadth, speed, control, and autonomy through scenario-based trade-offs. |
| GitHub draft pull requests are the appropriate review boundary. | The automation boundary must fit real review, evidence, permission, and governance practices. | Map target-user review workflows and test whether draft PRs provide sufficient context, access control, feedback, and approval separation. |
| Python CLI generation is a valid proving ground for the architecture. | The initial project class must exercise the core factory boundaries without hiding needs essential to later classes. | Compare CLI scenarios with anticipated project classes and identify which isolation, validation, evidence, and publication findings generalize or do not. |
| Codex remains replaceable behind a provider boundary. | Product governance and lifecycle semantics must not be inseparable from one execution provider. | Specify provider-neutral inputs, outputs, errors, evidence, and capabilities, then evaluate them against Codex and at least one hypothetical substitute. |
| Generated software can be validated without executing untrusted behavior outside controlled environments. | Safe verification depends on containing potentially unsafe generated dependencies, builds, tests, and commands. | Threat-model every validation and execution phase and prototype containment and egress controls against adversarial generated projects. |
| Users need retained prompts and evidence. | Retention affects trust, reproducibility, storage, confidentiality, and review usability. | Observe reviews and recovery exercises to determine which prompt, manifest, test, decision, and provenance records users actually need and for how long. |
| The experimental multi-agent system should not become the supported path until its boundaries are proven. | Premature promotion would couple the product to unvalidated orchestration, artifacts, and authority assumptions. | Define promotion criteria and test each candidate capability for bounded contracts, isolation, failure semantics, evidence, and explicit review ownership. |
| Future SDLC phases can be added as composable capabilities rather than one monolithic workflow. | The long-term governance model relies on independent evolution and reviewable phase boundaries. | Model representative lifecycle journeys, identify artifact handoffs and review gates, and test whether capabilities can be composed, replaced, paused, and resumed independently. |

