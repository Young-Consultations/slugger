# Interface Contract — GitHub Platform

## Purpose and responsibilities

GitHub is the organizational system of record for source references, routed automation, execution artifacts/evidence, branches, draft pull requests, checks, and human review decisions. GitHub owns service identity, repository object semantics, authorization enforcement, availability, and audit capabilities. Slugger owns the correctness and scope of requests it makes.

## Required capabilities and inputs

Slugger requires authenticated least-privilege capability to read configured source/target state and, only in the publication phase, create/update an authorized deterministic branch, commit verified content, and create/update/read a draft PR. A non-mutating verification mode requires read-only capability. Inputs include repository identity, base and requested head, expected ownership marker, verified files/commit message, draft PR content, source/correlation/delivery references, and evidence linkage. Credential scope is limited to the target and operation.

## Expected outputs

The platform must return stable repository/object references, observed base/head/commit state, PR identity/URL/state/draft status/body/markers, permission or conflict outcomes, and rate/service errors sufficient for Slugger to classify without exposing credentials. Actions/artifact delivery used by the control plane must preserve referenced run/artifact identity and access control.

## Required behavior

Slugger performs preflight reads, compares state to expected immutable ownership, mutates only after all gates, re-queries on create/update races, and confirms the resulting branch/PR. It does not depend on Actions concurrency as durable deduplication. It never automatically approves, marks ready, merges, releases, deploys, deletes a branch, closes a PR, or rewrites ambiguous user work.

## Failure, retry, and idempotency

Authentication/authorization, missing or protected base, unavailable/rate-limited service, write rejection, conflict, stale read, partial mutation, and ambiguous response produce a blocked/failed publication with durable evidence. Transient reads may retry with bounded backoff. Mutation retry first re-queries actual state and proceeds only if it proves convergence on the same delivery; it never blindly repeats. Partial branch creation without provable ownership is left for operator review.

## Security and data

Credentials are never available to generated code, provider, tests, PR body, artifact, or logs. Platform-delivered untrusted issue/PR text is treated as data, not instruction. Publication uses only verified inventory. Repository and branch protection remain authoritative and are not bypassed. Evidence links respect access classification.

## Versioning and portability

Slugger SHALL use supported platform behavior and record relevant API/contract version where exposed. Platform-breaking changes require adapter conformance and rollback. GitHub is a current organizational constraint; provider-neutral logical publication/evidence semantics SHOULD avoid unnecessary coupling, but no alternative platform is an MVP promise.

## Unknowns and validation

Validate authentication mechanism, token lifetime/scope, organization/repository policy, base protection, branch naming rules, PR/check requirements, artifact retention/limits, rate limits, outage objectives, audit access, fork behavior, API compatibility, and incident recovery for each deployment. No specific API endpoint or workflow implementation is prescribed by this requirements contract.
