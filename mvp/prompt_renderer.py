"""Deterministic Codex prompt rendering for the real CLI demo workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

_NAME_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
_RESERVED_PROJECT_NAMES = {"hello-codex"}


@dataclass(frozen=True)
class PromptInputs:
    project_name: str
    package_name: str
    demo_description: str
    output_dir: str = "generated-demo"


def validate_project_name(project_name: str) -> str:
    if not _NAME_RE.fullmatch(project_name):
        raise ValueError("project_name must be lowercase kebab-case")
    if project_name in _RESERVED_PROJECT_NAMES:
        raise ValueError("project_name is reserved for the canonical MVP demo")
    return project_name


def validate_description(description: str) -> str:
    if len(description) > 500 or any(ch in description for ch in "\x00\r"):
        raise ValueError("demo_description is too long or unsafe")
    if "```" in description or "${{" in description:
        raise ValueError("demo_description contains unsafe workflow/prompt delimiters")
    return description


def render_demo_prompt(
    *, project_name: str, demo_description: str, output_dir: str = "generated-demo"
) -> str:
    safe_name = validate_project_name(project_name)
    safe_description = validate_description(demo_description)
    package_name = safe_name.replace("-", "_")
    template = Path("prompts/mvp/github_actions_cli_demo_v1.md").read_text(
        encoding="utf-8"
    )
    return template.format(
        project_name=safe_name,
        package_name=package_name,
        output_dir=output_dir,
        demo_description=safe_description,
    )


def prompt_inputs(project_name: str, demo_description: str) -> PromptInputs:
    safe_name = validate_project_name(project_name)
    return PromptInputs(
        safe_name, safe_name.replace("-", "_"), validate_description(demo_description)
    )
