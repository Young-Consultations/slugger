<!--
  templates/Documentation.md
  Purpose: Template describing project documentation strategy, ownership, and structure.
-->

# Documentation Template

Project: [PROJECT_NAME]
Owner: [Documentation owner / role]
Last updated: [YYYY-MM-DD]

## Purpose
Describe what documentation exists, who it's for, and how it should be maintained. Make docs discoverable and accurate.

## Documentation types & locations
- User guides / onboarding: `docs/` or `site/` (public-facing docs)
- Architecture & design: `docs/architecture/`
- API docs: `docs/api/` or `specs/`
- Runbooks and runbooks/ on-call playbooks: `docs/runbooks/`
- Developer guide and contribution: `CONTRIBUTING.md` and `docs/dev/`

## Documentation standards
- Use Markdown or formats supported by your doc generator.
- Include examples, code snippets, and diagrams.
- Keep docs close to code when feasible (e.g., inline API docs, OpenAPI specs).
- Write for the intended audience: developer, operator, or end-user.

## Ownership & contributions
- Assign owners for major doc sections. Owners are responsible for keeping content current.
- Use PRs for doc changes and request at least one review.
- Use templates for new docs and issue templates to request docs updates.

## Versioning & releases
- Link docs to releases or branches for context where behaviour differs across versions.
- Archive deprecated docs with a clear notice and link to migration instructions.

## Search & discoverability
- Provide a central README or docs index with links to major sections.
- Enable search in generated sites (e.g., Algolia or built-in search).

## Quality & review
- Lint docs with markdownlint.
- Spell-check and run link-checker as part of CI.

## Localization (optional)
- If supporting multiple languages, maintain translation guidelines and separate folders per locale.

## Known gaps & backlog
- Track missing docs as issues labeled `documentation` and prioritize as part of roadmap.

