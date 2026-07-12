# Slugger 100% Completion Tasks

This package contains **14 dependency-ordered GitHub Agent tasks** designed to finish the
project by consolidating it onto one execution path and deleting obsolete code.

## Canonical final path

`slugger build` → `full-sdlc-v2` → managed prompts → capability resolver → ChatGPT planning →
Canva design/manual handoff → architecture/ADRs → real Codex agent → AppManifest →
ProjectMaterializer → IsolatedBuildRunner → bounded remediation → durable evidence/approvals →
readiness gate → GitHub draft PR → draft release candidate.

## 100% completion policy

The project is complete only when:

- All 14 tasks are merged.
- Every committed in-scope requirement has evidence.
- The clean-checkout offline acceptance suite passes.
- Both sample applications install and run.
- No alternate production execution path remains.
- No unresolved critical/high security finding remains.
- The installed wheel runs the same workflow as source.
- GitHub automation produces only draft, human-reviewable outputs.
- All obsolete code identified by these tasks is removed.

Run tasks in numeric order. GA-013 is final cleanup. GA-014 is final acceptance and certification.
