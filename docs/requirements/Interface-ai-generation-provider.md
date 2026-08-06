# Interface Contract — AI Generation Provider

> **Organization next-MVP restriction:** the production provider is Codex and may be invoked only for an authorized canonical `implement` request. `verify` and normal conformance CI never call Codex. The provider receives neither approval/routing authority nor publication credentials.

## Purpose and responsibilities

The provider supplies bounded candidate generation. Codex is the near-term provider named by the vision, but the contract is provider-neutral. The provider owns its service/model behavior, authentication, service availability and provider-side usage records. Slugger owns intent bounding, request construction, capability grants, workspace, policy, validation, evidence semantics, retries, and publication. Provider statements are claims, not verified results.

## Required provider capabilities

An approved adapter MUST support: identified provider/model or agent capability and version where available; non-interactive bounded invocation; explicit assigned working scope; supplied instructions/context; deadline/cancellation; restricted environment/capabilities; structured success/failure/timeout classification; safe bounded stdout/stderr or equivalent diagnostics; session/correlation and usage/cost metadata where available; and a detectable unsuccessful outcome. It MUST NOT require publication credentials or authority to approve policy.

## Inputs

Slugger supplies provider-neutral objective, normalized project identity/class, allowed context, output expectations, immutable request digest, prompt/policy version, workspace boundary, action/resource/network constraints, timeout/cancellation, and correlation reference. Only minimum required data is supplied. Secrets unrelated to provider authentication and protected portfolio data outside approved scope are prohibited.

## Outputs

Expected output is candidate content confined to the authorized workspace plus provider result category, timestamps/duration, session reference, provider/model/capability identity where exposed, usage/cost where exposed, and bounded safe diagnostics. Absence of optional metadata is explicit. A provider “success,” explanation, test claim, or confidence does not pass a Slugger gate.

## Events and data contract

Conceptual events are accepted, started, progress/heartbeat if available, completed, failed, timed out, and cancelled. Transport, SDK/CLI, streaming, and exact schema are implementation decisions. Adapter output MUST normalize semantics without fabricating unavailable values and retain raw diagnostic references only when safe and permitted.

## Failure behavior

Unavailable executable/service, authentication failure, rate/resource limit, policy refusal, malformed output, workspace escape attempt, timeout, cancellation failure, partial output, missing required capability, or unknown result yields a non-passing provider phase. Candidate partial output remains untrusted diagnostic material and is never published. There is no static/silent fallback presented as provider output.

## Retry and idempotency

Provider nondeterminism is expected. Product retry is explicit, bounded, and recorded as a new attempt under the same run/delivery lineage. Slugger rechecks authority and target preflight before retry and revalidates all new output. A completed matching delivery is reused before provider invocation. Automatic retry policy requires categorized transient failure, attempt/backoff limits, cost limits, and no policy/security violation.

## Security and privacy

Provider permissions are least-privileged and phase-limited. Generated code cannot read provider credential after generation. Requests/responses follow approved data classification, retention, residency and provider-use policies. Protected chain-of-thought is neither required nor retained; decision evidence consists of inputs, observable outputs, versions, checks, and accountable decisions.

## Versioning and substitution

Adapter and capability contract versions are recorded. Model/service changes that may affect output or security require compatibility assessment and regression evidence. A substitute must pass the same conformance suite for input, output, error, evidence, security, cancellation and resource semantics. Provider-specific features MAY be declared capabilities but MUST NOT silently change core policy.

## Unknowns and future validation

Validate supported Codex invocation surface, model/version pinning, data usage/residency/retention, cancellation guarantees, isolation needs, network behavior, rate and cost limits, session evidence, deterministic controls, availability, terms/licensing, incident notification, and alternate-provider feasibility. These are dependencies, not invented APIs.
