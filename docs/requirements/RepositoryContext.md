# Repository Context

## Purpose

`Young-Consultations/slugger` owns the Slugger AI Software Factory product: governed execution that converts approved, bounded software intent into validated, traceable, reviewable software artifacts. It is not `portfolio-tasks`; the latter is an external portfolio-governance product.

## Responsibilities

Slugger owns product-generation policy within its boundary; supported capability/scope declaration; execution intake enforcement; durable run/delivery correlation; isolated workspace lifecycle; constrained provider interaction; candidate inventory; validation; isolated dependency/install/test/smoke activity; evidence and status; retry/resume/idempotent consumption; and bounded deterministic draft publication. It also owns conformance evidence for its releases and the decision to keep experimental components outside the supported path.

## Boundaries and non-responsibilities

Slugger does not own organization-level schemas/vocabularies, repository registration or routing, portfolio intake/backlog/priority/execution approval, reusable consulting-method truth, provider model behavior, GitHub service behavior, target repository governance, human review/merge, release/deployment authority, or production operations for generated products. Slugger may verify external assertions before acting, but verification does not transfer ownership.

## Ownership

| Concern | Authoritative owner | Slugger role |
| --- | --- | --- |
| Product-generation requirements and execution policy | Slugger product owner | Author/enforce/evidence |
| Work intent, priority, approval | `portfolio-tasks` authority | Consume/reference/revalidate |
| Canonical contracts, registration, routing, compatibility | Organization `.github` control plane | Validate/consume/return result |
| Generated candidate and run evidence before handoff | Slugger | Own, protect, retain per policy |
| Target repository/base/user work | Target repository owner | Preflight; mutate only owned branch/draft |
| Generation algorithm/model | AI provider | Request bounded work; distrust result |
| Review, merge, release, deployment, production | Accountable humans/target owners | Supply evidence only |
| Consulting knowledge | `consulting-playbook` owner | Optional future versioned consumer |

## Internal capabilities

The required internal capability boundaries are intent/scope, contract and authority enforcement, run control, prompt provenance, provider gateway, workspace containment, artifact inventory/policy, dependency admission, isolated verifier, evidence/audit, publication adapter, status/diagnostics, configuration, and capability catalog. These are logical responsibilities, not mandated components or deployment units.

The current repository contains both an MVP and experimental multi-agent/full-SDLC material. Current code is blueprint evidence only. Experimental presence does not expand supported scope, satisfy a requirement, or authorize dependency from the MVP path.

## Data ownership

Slugger is authoritative for run IDs; its state transitions; effective Slugger policy/configuration identity; provider request digest/provenance; workspace ownership; generated inventory and integrity data; observed Slugger checks; safe diagnostics; and its publication attempt/result references. External identities and decisions are stored as attributed references/snapshots, never re-authored as Slugger truth. Target commits/PRs are authoritative in GitHub after publication; Slugger retains the correlated handoff record.

## External dependencies and consumers

Dependencies are the upstream portfolio authority, organization control plane/contract package, AI provider, GitHub platform, publication target, approved dependency sources, operating environment/containment, credential authority, and human reviewers. Optional future knowledge input may come from `consulting-playbook`. Consumers include requesting professionals, reviewers, operators, governance systems, test/assurance automation, downstream lifecycle capabilities, and future AI agents operating under approved contracts.

## Repository lifecycle responsibilities

This repository SHALL maintain requirements, threat and architecture decisions, implementation, tests, release evidence, supported/experimental labeling, migration/deprecation notices, operator/user documentation, vulnerability handling, and interface conformance for Slugger. It SHALL coordinate—but not unilaterally impose—cross-repository contract changes. It SHALL preserve backward compatibility for declared windows or explicitly reject unsupported versions. Removal or promotion of experimental code requires an approved boundary decision and evidence.

## Context model

```text
[Portfolio authority] --approved task reference--> [Organization control plane]
       (owns approval)       --canonical routed request--> [Slugger]
       (owns contract/routing)                         |
[AI provider] <---bounded generation request-----------|
[Dependency sources] <---policy-bounded acquisition----|
[GitHub / target repository] <---verified draft handoff|
       (owns repository and review)                    |
[Human authorities] <---evidence/status----------------+
```

All arrows require explicit contracts; no arrow implies shared database, source-tree access, workflow technology, or trust beyond the stated information.
