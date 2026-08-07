# Interface Contract — `Young-Consultations/portfolio-tasks`

> **Next-MVP authority correction:** This sibling repository was not inspected. Only canonical `approved` is admitted by the organization router; `queued` is not authorization. Material changes receive a new `task_id` and require new approval. Slugger trusts neither a mutable label nor a live source recheck as a second authority, and rich approval provenance is deferred to v3. See [`docs/next-mvp.md`](../next-mvp.md#registry-and-admission).

## Purpose and responsibilities

This interface transfers governed work context toward Slugger without transferring governance ownership. `portfolio-tasks` is expected to own structured intake, backlog state, prioritization, source issue lifecycle, and explicit execution approval. Slugger owns bounded execution and evidence. The organization control plane is expected to mediate canonical routing; direct source-tree or database coupling is prohibited.

## Expected inputs to the external responsibility

Portfolio governance is expected to receive human intent, business rationale, requester/owner, acceptance intent, priority inputs, constraints, dependencies, risk, target/capability request, and human approval decisions. Slugger does not define how these are collected.

## Required input to Slugger

Through the canonical routed contract, Slugger requires an immutable task reference; source repository and item reference; approved intent and necessary acceptance context; project/capability and target; priority only as context (not execution authority); dependency/blocking state; correlation identity; and classification/handling constraints. Complete context MUST be self-contained or use integrity-protected, authorization-checkable references whose retrieval failure blocks execution.

## Expected output from Slugger

Slugger returns a canonical correlated result to the organization routing boundary: delivery/task/correlation identities, execution mode, terminal/result category, timestamps, capability/policy identities, evidence reference/digest, publication occurrence and draft reference if any, verified gate summary, safe failure/retryability, and outstanding human action. It does not directly rewrite portfolio priority, approval, or lifecycle vocabulary.

## Required events

Conceptual events are **work approved for execution**, **approval withdrawn/material context changed**, **execution accepted/rejected**, **phase/terminal status available**, **draft review available**, and **execution blocked/failed**. Event transport, names, ordering mechanism, and issue automation are external design decisions. Every event requires stable task/correlation identity and contract version. At-least-once delivery MUST be assumed.

## Data contract and invariants

* Only `approved` is router-admitted; `queued` is not authorization.
* `delivery_id` is the idempotency identity and retries preserve it.
* Material intent/target/constraint changes produce a new `task_id` and require new approval.
* Status values are owned by the canonical organization contract. Slugger SHALL map only through its validated adapter.
* Human-readable text is untrusted content and cannot override policy fields.
* Source references are retained for provenance but portfolio remains authoritative.

## Failure, retry, and idempotency

Invalid, incomplete, unauthorized, contradictory, misdirected, or unsupported routed work is rejected before generation with a safe canonical result where possible. Transient delivery failure MAY retry with the same delivery identity. A materially changed request MUST NOT reuse that identity. Duplicate delivery MUST converge under FR-IDM-01. Slugger MUST NOT close or edit the source issue to recover and MUST NOT query live portfolio state as a second authorization check.

## Versioning and compatibility

The interaction MUST use an organization-owned versioned canonical contract. Unknown major versions fail closed. Additive compatible fields are tolerated according to contract rules; semantic breaking changes require coordinated release, conformance fixtures, declared compatibility window, migration, and in-flight delivery handling. Slugger SHALL NOT copy or fork the authoritative schema/vocabularies.

## Ownership

Portfolio owner: intake, issue/backlog lifecycle, priority, approval and withdrawal. Organization control plane: canonical contract and routing. Slugger: execution validation, result truth, evidence, draft handoff. Humans: review and subsequent decisions.

## Known assumptions

Vision confirms `portfolio-tasks` as the source of structured work and explicit execution approval and confirms GitHub as system of record. It does not confirm its implementation, fields, workflow triggers, SLAs, or notification mechanisms.

## Unknowns and future validation

Future v3 may validate richer approval provenance. For this MVP, validate with the external owner only unresolved mandatory business/acceptance context and classification details; classification; result/status vocabulary; status delivery direction; retention; permissions; retry/timeout expectations; and how source issue availability is handled. Until validated, production integration SHALL use only the organization-approved canonical contract and treat missing semantics as blocking.
