# Issue-to-Codex bridge retired

Local labels are not execution authority. Production work is accepted only through
the pinned organization router and canonical target workflow. Redelivery is
deduplicated by canonical delivery ownership, not labels or Actions concurrency.

Slugger no longer authorizes production Codex execution from local issues or labels. The former `codex-ready` issue-label bridge, repository-local issue contract parsing, `AUTHORIZED_CODEX_READY_ACTORS` approval variable, target allowlist, and local request identity have been retired to remove the duplicate control plane.

Production AI-SDLC work now originates in `Young-Consultations/portfolio-tasks`, where backlog intake and explicit approval are owned. Routing is owned by the organization control plane in `Young-Consultations/.github`.

Slugger is only a target executor. The registered production target workflow is:

```text
Young-Consultations/slugger/.github/workflows/codex-execute.yml@main
```

The supported organization contract is `ai-sdlc-contract/v2`, and Slugger pins the organization control-plane checkout to `ai-sdlc-v2.1.0`. Slugger consumes the `ai_sdlc_contracts` package from that immutable release instead of copying schemas or validators locally.

The target workflow supports two modes:

- `verify`: validates canonical input, checks Slugger authorization and workflow wiring, runs safe non-mutating checks, and emits a canonical result without invoking Codex, changing branches, committing, pushing, or publishing.
- `implement`: runs controlled Slugger generation and validation, then creates or updates exactly one deterministic draft pull request. Automated publication remains draft-only; Slugger never merges generated code or marks generated pull requests ready for review.

Organization-side follow-up is required before enabling Slugger in the registry; this repository does not enable the registry entry itself.
