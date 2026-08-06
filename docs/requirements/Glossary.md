# Authoritative Glossary

| Term | Definition |
| --- | --- |
| Acceptance criterion | Observable, pass/fail condition that demonstrates a requirement outcome; it is not a provider claim. |
| Accountable human | Identified person authorized by governance to make a consequential decision and remain responsible for it. |
| AI Software Factory | Slugger product boundary that applies governed AI assistance and engineering verification to transform approved intent into reviewable software artifacts. |
| Approval | Explicit, attributable, current human/governance decision scoped to identified content and action. A label or AI assertion is not sufficient unless the canonical authority defines and attests the decision. |
| Artifact | Identifiable, versioned or integrity-addressed input, output, evidence, or lifecycle work product. |
| Artifact manifest | Protected inventory of candidate artifacts and their normalized identities, sizes/types, integrity digests, provenance and policy dispositions. |
| Bounded capability | A lifecycle function with explicit versioned inputs/outputs, allowed actions, limits, validation, evidence, failures, compatibility, owner and human review point. |
| Candidate | Untrusted provider-generated content not yet established as valid or publishable. |
| Canonical contract | Versioned organization-owned definition of cross-repository data and semantics. Slugger consumes but does not own it. |
| Capability catalog | Controlled declaration of supported, deprecated, experimental and future project classes/capabilities and their promises. |
| Claim | Statement supplied by a user, provider, generated artifact, or external actor that has not been independently observed by the relevant Slugger check. |
| Complete context | All canonical identities, authority, intent, constraints, target, acceptance and handling information necessary for a bounded decision without implicit local assumptions. |
| Controlled isolation | Environment whose filesystem, process, network, credentials, time, storage and outputs are bounded according to approved policy for untrusted behavior. |
| Correlation ID | Stable identifier relating work and evidence across repositories, systems and phases; it is distinct from a single runtime attempt. |
| Delivery ID / idempotency key | Canonical stable identity for one logical routed delivery and its durable ownership. It is never a workflow run/attempt ID. |
| Deterministic branch | Contract-defined branch identity derived from stable governed inputs, not time, randomness or runtime attempt. |
| Draft pull request | GitHub review object not marked ready for merge; Slugger's maximum automated publication boundary. |
| Evidence | Integrity-verifiable record of observable input, action, result, environment, version, decision or status. |
| Evidence package | Human- and machine-consumable correlated collection supporting review of a run, including limitations and outstanding decisions. |
| Experimental | Available for research but not a supported product promise, release path, or evidence of conformance. |
| Fail closed | Deny dependent action when authorization, safety, validity, identity, ownership, evidence, or system state is failed, missing, stale, contradictory or uncertain. |
| Gate | Required policy/verification decision that must pass with current evidence before a dependent lifecycle transition. |
| Generated project | Candidate or verified software project created within a run; it is distinct from Slugger source. |
| Human review boundary | Point at which automation supplies a draft/evidence and a person independently decides progression. |
| Immutable-input digest | Integrity identity of all fields whose change would alter authority, execution, validation or publication ownership. |
| Logical request | Governed work intent/revision independent of transport attempts. |
| MVP | Initial supported Slugger boundary: governed generation and verification of a bounded dependency-minimal Python CLI project and draft review handoff. |
| Organization control plane | External `.github` responsibility for canonical contracts, registration, routing, compatibility and control-plane verification. |
| Portfolio governance | External responsibility for intake, backlog, priority, dependencies and explicit execution approval. |
| Production-ready | Approved state supported by complete security, operational, compliance, release and accountable human decisions; Slugger's MVP checks alone never establish it. |
| Project class | Governed category of generated system with declared inputs, output promise, constraints and validation profile. |
| Provider | Replaceable external AI execution capability that returns untrusted candidate output. |
| Publication | Authorized transfer of exact verified artifacts/evidence to a deterministic branch and managed draft PR; it excludes merge/release/deployment. |
| Residual risk | Risk or decision not resolved by performed checks and explicitly left to an accountable human. |
| Resume | Continue from a previously recorded trustworthy boundary after revalidating affected conditions. |
| Retry | New attempt of a failed/interrupted operation under recorded lineage and bounded policy. |
| Run | One Slugger execution record with unique ID, attempts, state, artifacts, evidence and outcome, related to a logical delivery. |
| Run attempt | Distinguishable execution effort within retry/resume lineage; not publication ownership. |
| Scope declaration | Run-specific statement of accepted objective, supported class, constraints, promised checks, exclusions and human obligations. |
| SDLC | Software development lifecycle from vision/requirements through design, implementation, verification, release, operation and learning. |
| Slugger-managed | Ownership proven through the complete expected deterministic identity and valid machine marker, not merely a name prefix. |
| Smoke verification | Deterministic, non-interactive observed check of the project class's minimum promised executable behavior. |
| Source issue/reference | External portfolio work record linked for provenance; Slugger does not own its lifecycle. |
| Supported | Product capability with approved scope, controls, documentation, conformance evidence, owner and release commitment. |
| Target repository | Authorized GitHub repository receiving a verified draft; its owner retains repository governance. |
| Telemetry | Operational measurements optionally exported beyond local run evidence; it excludes mandatory local evidence and must not expose sensitive content. |
| Terminal state | Truthful final outcome for an attempt/run according to applicable canonical semantics; it does not necessarily mean business work is complete. |
| Verified fact | Claim supported by a specified observed check and retained evidence, limited to that check's scope. |
| Workspace | Run-specific contained location for generated-project activity, outside Slugger source and protected systems. |
