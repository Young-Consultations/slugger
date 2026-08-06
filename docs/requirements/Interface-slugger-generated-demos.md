# Interface Contract — `Young-Consultations/slugger-generated-demos`

## Purpose and responsibilities

This repository is a known sandbox publication target for generated project drafts. It is expected to own its base branch, access policy, review/merge decisions, retention, and any downstream repository automation. Slugger owns only its deterministic generated branch and demonstrably managed draft PR for the relevant logical request. The contract also applies to another approved target repository unless its stricter policy supersedes it.

## Expected input to Slugger

Slugger requires canonical target identity, authorized base, deterministic requested branch, stable delivery/publication identity, target policy/classification, and least-privileged credential supplied only to target preflight/publication. The target MUST be approved for generated drafts and either safe under its policy or already provably managed for the same identity.

## Required outputs to the target

Only verified inventoried candidate files plus approved reviewer evidence/metadata may be committed. Publication produces a deterministic branch, commit identity, machine-readable ownership marker, and exactly one open managed **draft** PR containing source/correlation/delivery references; contract/policy identity; scope; verified checks and evidence digest/reference; exclusions/residual risk; and required human action. Secrets, runtime environments, unbounded logs, internal credentials, provider control files, and unverified files MUST be absent.

## Required events

Conceptual events: target preflight classified, branch/draft created, matching managed draft updated/reused, publication blocked, human review/merge/close performed externally. Slugger observes external state but MUST NOT react to merge/close by silently recreating work.

## Ownership and data contract

Branch and PR ownership is proven only by the expected deterministic branch plus a validated machine marker whose immutable fields bind delivery, correlation, source, target, contract, base, requested branch, and input/evidence digest. Names alone are insufficient. Slugger MUST preserve target-owned files and MUST limit mutation to the proven managed branch. Target state is authoritative after handoff; Slugger keeps evidence of what it published.

## Failure behavior

Missing repository/base, insufficient permissions, unsafe nonempty target, branch without proven ownership, conflicting marker/input, wrong base/head, multiple matching PRs, non-draft match, closed/merged match, protection failure, race not converging on the expected owned draft, or service ambiguity MUST fail closed. Existing objects remain untouched for a human. Automation MUST NOT delete branches, close PRs, rewrite unowned history, force push user work, or guess ownership.

## Retry and idempotency

Preflight occurs before expensive generation and immediately before mutation. Matching complete open managed work is reused without regeneration; a safe matching draft may be updated with the latest fully verified output under approved policy. Concurrent creates re-query and converge only on one structurally valid owned draft. A logical retry preserves stable identity and does not use workflow attempt IDs for ownership.

## Versioning

Ownership marker and evidence formats MUST be versioned. Readers must tolerate contract-approved additive fields, reject unknown major/required semantics, and support an explicit migration period for known legacy markers without weakening proof. Target policy changes that invalidate evidence require revalidation.

## Known assumptions and unknowns

Existing Slugger documentation names this repository as the separate demonstration target; the repository itself was not inspected. Validate its owner/CODEOWNERS, base and protection rules, allowed content/license, environment/secrets, PR automation, cleanup/retention, whether multiple generated projects share one repository, size/rate limits, reviewer SLAs, and incident/recovery ownership. No production or general target suitability is inferred from its name.
