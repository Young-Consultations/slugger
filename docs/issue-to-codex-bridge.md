# Slugger Issue-to-Codex Automation Bridge

The issue bridge connects a synchronized Slugger issue to the canonical user-idea Codex workflow. It is intentionally approval gated: only applying `codex-ready` to an eligible open issue can call the reusable Codex workflow.

## Required issue contract

Issue text is treated as hostile input. The bridge accepts only the exact portfolio source marker and bounded deterministic field markers:

```markdown
<!-- portfolio-task-source: Young-Consultations/portfolio-tasks#123 -->
<!-- slugger-field: idea -->Build a small CLI.<!-- /slugger-field: idea -->
<!-- slugger-field: project_name -->small-cli<!-- /slugger-field: project_name -->
<!-- slugger-field: target_repository -->Young-Consultations/slugger-generated-demos<!-- /slugger-field: target_repository -->
```

The current target repository allowlist is reviewable in `.github/slugger/target-allowlist.json`.

## Manual setup steps

Operators must configure these items before the first live controlled execution:

1. Create any missing issue labels: `portfolio-task`, `codex-ready`, `codex-running`, `codex-complete`, and `codex-failed`.
2. Configure authorized maintainers or teams by setting the `AUTHORIZED_CODEX_READY_ACTORS` repository variable to a comma-separated list of GitHub logins allowed to apply `codex-ready`.
3. Configure `OPENAI_API_KEY` only on the protected `codex-demo` environment used by the canonical Codex job.
4. Configure `SLUGGER_GITHUB_TOKEN` with the least target-repository permissions needed for validation and draft pull request publication.
5. Configure the `codex-demo` protected environment.
6. Select required reviewers for the protected environment.
7. Perform the first live controlled execution with a sandbox issue and an allowlisted sandbox target repository.

Do not auto-merge generated pull requests and do not push generated content directly to `main`.
