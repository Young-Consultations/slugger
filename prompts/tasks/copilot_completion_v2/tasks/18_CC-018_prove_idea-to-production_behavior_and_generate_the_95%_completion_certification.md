# CC-018: Prove idea-to-production behavior and generate the 95% completion certification

**Milestone:** M9 — Acceptance  
**Priority:** P0  
**Implementation order:** 18  
**Depends on:** CC-015, CC-016, CC-017

## Copilot Agent assignment

Act as both:
- a senior Python software engineer responsible for executable, secure, maintainable behavior; and
- a senior prompt engineer responsible for versioned, testable, structured AI instructions.

Complete this task in one focused draft pull request.

## Read first

- `prompts/tasks/copilot_completion_v2/MASTER_COPILOT_AGENT_PROMPT.md`
- `prompts/tasks/copilot_completion_v2/OFFICIAL_INTEGRATION_REFERENCES.md` when external services are involved
- Applicable system prompts and ADRs
- Current source and tests named in this task

## Objective

Create deterministic acceptance scenarios that prove Slugger transforms an idea into a runnable, tested, secure, traceable, approved, packaged Python application, then calculate completion from evidence.

## Verified current-state problem

- The repository has component tests but no acceptance suite proving the central product promise.
- Prior completion percentages were qualitative.

## Primary scope and likely files

- tests/acceptance/
- examples/
- models/manifest.py
- observability/reporter.py
- docs/ai-sdlc-spec.md
- docs/production-readiness.md
- README.md

The file list is guidance. Inspect call sites and change only what is required.

## Ordered implementation instructions

1. Create at least two acceptance scenarios: task-tracker CLI and FastAPI service.
2. Use deterministic mock ChatGPT, Codex, Canva, and GitHub adapters while exercising the same runtime contracts.
3. Run the entire workflow from `ProjectInput` through draft release candidate.
4. Restart the process mid-run and resume.
5. Inject planning validation failure, Codex defect, failing test, security finding, provider transient failure, approval rejection, and GitHub check failure; verify remediation/escalation.
6. Install and smoke-run the final generated applications.
7. Assert complete artifact lineage, requirements traceability, prompt/provider provenance, audit records, readiness evidence, package/SBOM, rollback instructions, and release candidate.
8. Create a canonical requirements catalog and machine-generated completion report.
9. Require at least 95% of committed in-scope requirements complete and 100% of P0 mandatory requirements.
10. Document residual risks, unsupported modes, runbooks, backup/restore, incident response, and rollback.
11. Add opt-in live-provider smoke tests outside the standard acceptance job.

## Prompt-engineering requirements

- Acceptance fixtures must validate prompt input/output contracts and malformed-response behavior.
- No generated narrative may substitute for asserted evidence.

## Software-engineering requirements

- Standard acceptance tests require no live network or credentials.
- Do not count optional future roadmap items in the in-scope denominator.
- A deferred P0 requirement prevents certification.

## Acceptance criteria

- Both generated applications install and run.
- Restart/resume and every seeded failure path are proven.
- The report shows at least 95% overall and 100% P0 completion from linked evidence.
- A clean checkout passes all CI-equivalent and acceptance commands.

## Required validation

- `python -m pytest tests/acceptance -q`
- `python -m pytest -q`
- Run all documented lint, type, coverage, security, package, and workflow validation commands
- Generate the completion certification report

## Pull-request evidence

- Acceptance harness
- Two complete samples
- Failure injection
- Requirements catalog
- Certification and runbooks

## Out of scope

- New language support
- Enterprise SLA
- Independent third-party audit

## Rollback requirement

Do not issue certification. Preserve the latest passing release candidate and publish a blocker report.

## Definition of Done

This task is done only when:

1. Every acceptance criterion has objective evidence in the draft pull request.
2. Every required validation command passes or an explicitly approved platform limitation is documented.
3. The complete repository test suite passes.
4. New behavior is exercised through the primary orchestration path, not only through isolated unit tests.
5. Documentation, configuration examples, prompt metadata, and migrations are updated.
6. No secret, credential, private token, or sensitive generated content appears in committed files or logs.
7. The task has not introduced a duplicate subsystem or an unbounded retry/agent loop.
8. The pull request remains draft until human review is complete.

## Git guidance

- Branch: `copilot/cc-018`
- Commit: `CC-018: Prove idea-to-production behavior and generate the 95% completion certification`
- Draft PR: `CC-018 — Prove idea-to-production behavior and generate the 95% completion certification`
