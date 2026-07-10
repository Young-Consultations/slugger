# prompts/

This directory contains the prompt library for the Slugger system.

## Purpose

Prompts are first-class engineering assets. They are versioned, reviewed, documented, and continuously improved like source code.

## Structure

| Path | Contents |
|------|----------|
| `system/` | Permanent operating guidance for all AI agents |
| `tasks/` | Task-specific prompt files for SDLC phases |
| `templates/` | Reusable prompt templates with variable substitution |

## Conventions

- Prompts are written in Markdown.
- Prompt files are named descriptively (e.g., `generate_requirements.md`).
- System prompts define global agent behavior and are rarely changed.
- Task prompts are scoped to a specific workflow phase or artifact type.
- Templates use `{{variable_name}}` placeholders for dynamic content.
- Every prompt includes a version comment and description header.

## Related

- `agents/` — agents that use prompts from this library
- `knowledge/prompt-engineering/` — knowledge articles on prompt design
- `templates/` — document templates (distinct from prompt templates)
