# Configuration Architecture

## Configuration domains

| Domain | Examples | Owner / mutability |
|---|---|---|
| Product policy | Supported capability profiles, mandatory gates, draft-only boundary | Product/security-approved release artifact; not runtime-weakenable |
| Integration | Contract releases, endpoints, adapter selection, target allowlists | Integration owner; validated per environment |
| Operational | Concurrency, quotas, timeouts, retry bounds, workspace/retention, telemetry | Operator within product-enforced ranges |
| Project-class | Output limits, structure, commands, dependency policy, smoke contract | Versioned capability profile |
| Presentation | Output format, locale/accessibility, safe verbosity | User/operator, no semantic change |
| Secrets | Provider/target/store credentials | Credential authority; references only in configuration |

## Precedence

From strongest to weakest: (1) non-overridable requirements/security invariants embedded in signed/released policy; (2) capability profile; (3) environment/deployment config; (4) explicitly authorized per-request choices within profile; (5) safe defaults. Secret values are resolved separately and never merged into serializable effective configuration. CLI/environment variables cannot override mandatory policy or grant support/approval.

## Resolution and validation

Resolve into an immutable typed `EffectiveConfiguration` before accepting/advancing a run. Validate schema, semantic ranges, mutual constraints, adapter/capability compatibility, paths/endpoints, required credential references and unknown fields. Compute a redacted canonical digest and record source/provenance/version. Invalid, missing or ambiguous mandatory configuration fails startup/readiness or the affected request before side effects.

## Defaults

Defaults are deny, no unsupported capability, draft only, least privilege, no generated network, bounded resources/output/retry, no sensitive telemetry, and conservative retention until approved policy. A default must be documented, testable and included in the effective digest; hidden behavioral defaults are prohibited.

## Change and reload

Classify changes as dynamic-safe, next-run, restart-required, or breaking. Active runs remain pinned to accepted config/profile; a security revocation may block progression and must be recorded, never silently reinterpret history. Changes that affect candidate, gate, authority, isolation, dependency or publication invalidate corresponding evidence. Rollout requires validation/canary, audit, rollback and in-flight handling.

## Environment and tenancy

Environment-specific config is separated from source and from generated artifacts. Production refuses test/mock adapters and unapproved targets. If multiple tenants/classifications are later supported, configuration and credentials are isolated and identity includes the policy context; cross-tenant caches/state/evidence are forbidden absent explicit safe design.

## AI-agent rules

Agents may propose configuration changes but cannot activate policy exceptions, capability promotion or secrets. Generated configuration is untrusted candidate content. Machine-readable schemas document purpose, type, constraints, sensitivity, default, owner, reload behavior and requirement trace for every setting.
