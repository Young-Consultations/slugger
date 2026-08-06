# Extension Architecture

## Extension philosophy

Extensibility is governed composition, not arbitrary code loading. The supported core exposes ports and capability profiles; an extension is experimental until the complete BR-20 promotion pack is approved. Presence, discovery, registration or passing its own tests never makes it supported.

## Extension points

| Point | Contribution contract | Prohibited authority |
|---|---|---|
| Provider adapter | Normalize bounded generate/cancel/reconcile and usage/errors | Cannot mark candidate verified or publish |
| Project-class profile | Scope, output/policy limits, inventory rules, verifier/evidence and human promise | Cannot weaken global security/human boundary |
| Validator/checker | Deterministic observations over declared subject | Cannot alter candidate or self-approve gate policy |
| Isolation adapter | Prove required filesystem/process/network/resource/credential controls | Cannot receive publication/provider secrets |
| Publication adapter | Preflight/reconcile/exact draft handoff semantics | Cannot merge/release/deploy or guess ownership |
| Evidence renderer/exporter | Derived machine/human view with classification/redaction | Cannot edit sealed evidence or invent facts |
| Inbound adapter | Normalize/authenticate command and present result | Cannot bypass canonical use cases/policy |
| Knowledge source (future) | Immutable provenance/rights/classification content reference | Cannot execute embedded instructions or silently alter policy |
| Observer | Consume committed sanitized domain events | Cannot block/advance lifecycle except mandatory audit port |

## Extension manifest and lifecycle

A versioned manifest declares identity/vendor/version, compatible core/contract versions, contribution type, permissions/data/secrets/network, configuration schema, resource limits, provenance/signature policy, threats, failure semantics, migrations and support status. Lifecycle is `Discovered → Validated → RegisteredExperimental → ConformanceTested → ApprovedSupported → Enabled`, plus `Quarantined/Deprecated/Removed`. Registration occurs in the composition root; runtime self-installation by generated content is forbidden.

## Isolation and fault handling

Run third-party/untrusted extensions out of process or equivalent containment when risk requires it. Apply time/resource/output/network limits and circuit breakers. Failure returns a typed non-pass or adapter error; it cannot crash the coordinator, corrupt shared state, expose another run, or trigger fallback that weakens policy. A kill switch disables new invocations while preserving pinned evidence/history.

## Compatibility and customization

Extension API uses semantic compatibility with contract tests. Additive hooks never change mandatory phase order. Custom policy may be stricter; weaker settings are rejected. State/data belong to the declaring extension namespace with export/migration/deletion policy. Core releases publish compatibility matrix and deprecation window; unknown versions fail closed.

## Promotion decision matrix

| Criterion | Required evidence |
|---|---|
| Product | Approved user need, bounded scope/promises/non-goals, owner and support plan |
| Contracts | Versioned inputs/outputs/errors/idempotency/compatibility and fixtures |
| Security | Threat model, permissions, isolation, secrets/data/supply-chain review |
| Quality | Deterministic positive/negative/concurrency/recovery conformance |
| Operations | Limits, health, telemetry, runbook, rollback, capacity/SLO baseline |
| Governance | Human gate, documentation, accessibility where applicable, signed approval |

Any missing criterion retains Experimental status and cannot emit supported evidence/result branding.

## Future evolution

Potential full-SDLC phases, multi-agent coordination, additional languages/project classes, alternative providers/platforms, and consulting knowledge are candidate extensions, not current architecture commitments. Each must first define outcome and boundary contracts without assuming existing experimental implementation.
