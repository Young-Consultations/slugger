# Interface Contract — `Young-Consultations/consulting-playbook`

## Purpose and status

The consulting repository is expected to own reusable methods, assessments, and delivery playbooks. It is **not an MVP runtime dependency**. This contract governs only a future approved use of consulting knowledge by a promoted lifecycle capability; locally present consulting material does not prove synchronization with that external repository.

## Repository responsibilities

The playbook owner is expected to curate content, provenance, applicability, version/release identity, license/use restrictions, sensitivity, deprecation/supersession, and quality approval. Slugger would own selection for an approved run, faithful attribution, policy enforcement, transformation traceability, and validation of derived artifacts. Slugger MUST NOT silently edit or declare authoritative consulting content.

## Required inputs and outputs

Future input requires immutable content/release identity, artifact identity/type, version, provenance/owner, applicability and exclusions, review status, classification/license, integrity digest, dependency links, and compatibility metadata. Slugger output would contain cited source identities/versions, selection rationale, transformation provenance, derived artifact and validation/review state, limitations, and feedback/change proposal. Transport and schema remain undecided.

## Events and contracts

Conceptual events are content release, deprecation/supersession, compatibility change, approved import, and feedback proposal. A run MUST pin content identity; an upstream change never silently changes active or historical output. Unapproved/draft content SHALL NOT be presented as authoritative. Human-provided client data must remain governed by classification and consent.

## Failure, retry, and idempotency

Unavailable, unverifiable, incompatible, restricted, ambiguous, or superseded content blocks only the dependent future capability and cannot affect MVP generation. Retry preserves the selected version. Re-import of the same digest is idempotent; changed content receives a new identity/version and triggers downstream impact analysis where applicable.

## Versioning and ownership

The playbook owner controls content versions and semantics. Slugger controls its adapter and derived artifact. Breaking metadata/semantic changes require a new incompatible version and migration guidance. There is no assumed API, workflow, shared filesystem, submodule, or issue protocol.

## Unknowns and future validation

Before integration, validate authoritative repository/release, content taxonomy, review status, licensing, client confidentiality, update cadence, retrieval/authentication, schema/format, citation rules, feedback governance, deletion/retention, compatibility policy, and outage expectations. Requirements and threat analysis for the consuming capability must be approved first.
