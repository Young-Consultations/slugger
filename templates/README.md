# templates/

This directory contains reusable document templates for artifacts, reports, and generated outputs.

## Purpose

Templates standardize the structure of generated artifacts, ensuring consistency across workflow runs. They decouple document structure from the agents that populate them.

## Conventions

- Templates are written in Markdown with `{{variable_name}}` placeholders.
- Each template includes a header comment describing its purpose and required variables.
- Templates are versioned; breaking changes increment the template version.
- Template filenames are descriptive and use `snake_case`.

## Typical Contents

- `requirements.md` — requirements document template
- `user_story.md` — user story template
- `architecture.md` — architecture document template
- `adr.md` — Architecture Decision Record template
- `test_plan.md` — test plan template
- `release_notes.md` — release notes template
- `risk_register.md` — risk register template

## Related

- `prompts/templates/` — prompt templates (distinct from document templates)
- `agents/` — agents that render templates to produce artifacts
- `artifacts/` — rendered artifact outputs
