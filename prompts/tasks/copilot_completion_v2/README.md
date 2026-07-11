# Slugger GitHub Copilot Completion Plan v2

## Why this plan replaces the earlier backlog

The earlier backlog was broad and component-oriented. It allowed an agent to add classes and tests
without proving that Slugger could perform its central job.

This revision is organized as **18 vertical, dependency-ordered tasks**. Every P0 task must produce
evidence through the primary runtime path. The plan starts by correcting false-success behavior,
then connects real agents, creates a runnable project, executes quality gates, secures persistence
and approvals, and ends with idea-to-release acceptance tests.

## Verified repository baseline

- Archive reviewed: `slugger-main 5.zip`
- Verified on: July 11, 2026
- Test suite: **443 passed**
- Existing pytest collection warnings: **7**
- Current classification: AI-SDLC framework prototype
- Central missing proof: idea → runnable, tested, secure, traceable, approved, packaged Python app

## Folder contents

- `MASTER_COPILOT_AGENT_PROMPT.md` — mandatory operating rules for every Copilot session
- `OFFICIAL_INTEGRATION_REFERENCES.md` — current official OpenAI, Canva, and GitHub references
- `IMPLEMENTATION_ORDER.md` — task sequencing and limited parallelism guidance
- `REQUIREMENTS_COMPLETION_MATRIX.yaml` — evidence-backed completion calculation
- `tasks/` — one copy-ready prompt per pull request

## How to use

1. Copy `prompts/tasks/copilot_completion_v2/` into the Slugger repository.
2. Start with CC-001.
3. Give Copilot Agent:
   - the master prompt;
   - the assigned task file;
   - repository access.
4. Require a draft PR and review its plan before accepting broad changes.
5. Merge only when the task's Definition of Done is proven.
6. Update the requirements matrix with evidence after merge.
7. Do not claim 95% completion until CC-018 generates the certification report.

## Project manager release rule

- All P0 tasks must be complete.
- Overall evidence-backed completion must be at least 95%.
- The final acceptance scenarios must pass from a clean checkout.
- There may be no unresolved critical/high security issue without an approved, unexpired waiver.
- A draft release candidate is not a production release.
