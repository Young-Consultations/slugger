# Error Handling Strategy

## Taxonomy

| Category | Examples | Default retry | Effect |
|---|---|---|---|
| Contract/Input | malformed, incomplete, unsupported major/mode | No until corrected/new approved revision | Reject before mutation |
| Authority/Governance | missing/stale/withdrawn approval, unregistered target | No; transient verification outage may retry | Block consequential action |
| Policy/Security | unsafe path/content/dependency, secret, control unavailable | No; correction creates/revalidates affected work | Fail closed, incident if disclosure |
| Identity/Conflict | same delivery/different digest, lease/version conflict | Reconcile; semantic conflict no | Preserve state, human action if unresolved |
| Provider | rate limit, timeout, rejection, partial/ambiguous response | Bounded only when categorized and budget permits | Never treat partial candidate as verified |
| Infrastructure | store full/unavailable, sandbox startup, filesystem | Bounded with deadline; required evidence/store failures block | Resume from durable boundary |
| Verification | install/test/smoke failure or timeout | Usually no automatic retry unless nondeterminism policy allows | Non-pass; no publication |
| Publication | permission/rate/outage, race, ambiguous ownership | Reconcile first; retry definite safe transient calls | Preserve target; no regenerate/delete/force |
| Cancellation | human/governance/deadline | No | Stop new effects, record/cleanup safely |
| Internal defect | invariant violation/unmapped exception | No blind retry; alert | Safe terminal/error state, retain diagnostics |

## Error contract

An `ErrorRecord` contains stable category/code, phase/component, safe message, diagnostic/evidence reference, retryability and prerequisites, first/last observation, external correlation, cause chain, affected gate/evidence bindings, and required human action. It excludes secrets/raw untrusted output. Public adapters map it to canonical vocabulary without losing the local record.

## Propagation and isolation

Adapters translate vendor errors once at the boundary. Domain/application methods return typed outcomes for expected failures and reserve invariant faults for defects. Coordinator persists the observation before transitioning. Failure of one run cannot modify another; provider/sandbox failure cannot reach publication; observability failure cannot hide mandatory evidence failure. Batch/child aggregation, if promoted later, cannot convert a child failure into success.

## Retry policy

Retry only if the category is transient, input is identical, authority/policy remains current, operation is idempotent or reconciled absent, deadline/attempt/cost budget remains, and retry cannot bypass a gate. Use capped exponential backoff with jitter and circuit breaking. Record each attempt. Re-run all downstream checks invalidated by output, environment, configuration, tool or policy changes.

## Recovery and compensation

Recovery loads last committed boundary, validates record integrity and current policy, reconciles pending external operations, and continues or blocks. Compensation is conservative: release local leases, revoke credentials, terminate sandbox and ownership-proven cleanup. Slugger does not compensate by deleting branches, closing PRs, force pushing, editing portfolio records, or concealing partial state.

## User experience

Every terminal or blocked result answers: what was attempted; what was observed; what did not run; whether target mutation occurred; whether retry/resume is safe; where sanitized evidence resides; what data/resources remain; and who must act next. Do not expose stack traces by default or claim production readiness.
