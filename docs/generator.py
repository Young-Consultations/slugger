"""Documentation generator — produce reference docs from agent and workflow metadata.

:class:`DocGenerator` introspects registered agents and workflow definitions
and emits Markdown reference pages suitable for inclusion in ``docs/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AgentDocPage:
    """Generated documentation for a single agent.

    Parameters
    ----------
    agent_name:
        Canonical agent name.
    category:
        Agent category (e.g. ``'planning'``).
    description:
        Agent description.
    inputs:
        Declared input names.
    outputs:
        Declared output artifact names.
    capabilities:
        Capability names.
    version:
        Agent version string.
    """

    agent_name: str
    category: str
    description: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    version: str = '1.0.0'

    def to_markdown(self) -> str:
        """Render the page as Markdown."""
        lines = [
            f'# {self.agent_name}',
            '',
            f'**Category:** {self.category}  ',
            f'**Version:** {self.version}',
            '',
            '## Description',
            '',
            self.description or '_No description provided._',
            '',
        ]
        if self.inputs:
            lines += ['## Inputs', '']
            for name in self.inputs:
                lines.append(f'- `{name}`')
            lines.append('')
        if self.outputs:
            lines += ['## Outputs', '']
            for name in self.outputs:
                lines.append(f'- `{name}`')
            lines.append('')
        if self.capabilities:
            lines += ['## Capabilities', '']
            for cap in self.capabilities:
                lines.append(f'- `{cap}`')
            lines.append('')
        return '\n'.join(lines)


@dataclass
class WorkflowDocPage:
    """Generated documentation for a single workflow definition."""

    name: str
    version: str
    description: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the page as Markdown."""
        lines = [
            f'# Workflow: {self.name}',
            '',
            f'**Version:** {self.version}',
        ]
        if self.tags:
            lines.append(f'**Tags:** {", ".join(self.tags)}')
        lines += [
            '',
            '## Description',
            '',
            self.description or '_No description provided._',
            '',
            '## Steps',
            '',
        ]
        for i, step in enumerate(self.steps, start=1):
            lines.append(f'### {i}. {step.get("name", "step")}')
            if step.get('description'):
                lines.append(step['description'])
            if step.get('agent'):
                lines.append(f'**Agent:** `{step["agent"]}`')
            if step.get('outputs'):
                lines.append(f'**Outputs:** {", ".join(f"`{o}`" for o in step["outputs"])}')
            lines.append('')
        return '\n'.join(lines)


class DocGenerator:
    """Generate Markdown documentation from agent and workflow metadata.

    Parameters
    ----------
    output_dir:
        Directory where documentation files are written.

    Examples
    --------
    >>> gen = DocGenerator(Path('docs/reference'))
    >>> gen.generate_agent_docs(registry)
    >>> gen.generate_workflow_docs(recipe_dir)
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Agent documentation
    # ------------------------------------------------------------------

    def generate_agent_docs(self, registry: Any) -> list[Path]:
        """Write one Markdown file per agent in *registry*.

        Parameters
        ----------
        registry:
            :class:`~agents.registry.AgentRegistry` instance.

        Returns
        -------
        list[Path]
            Paths of the generated files.
        """
        agents_dir = self.output_dir / 'agents'
        agents_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []
        for name in registry.list():
            agent = registry.resolve(name)
            meta = agent.metadata
            page = AgentDocPage(
                agent_name=meta.name,
                category=getattr(meta, 'category', 'unknown'),
                description=getattr(meta, 'description', ''),
                inputs=getattr(meta, 'inputs', []),
                outputs=getattr(meta, 'outputs', []),
                capabilities=[c.name for c in agent.capabilities],
                version=meta.version,
            )
            out = agents_dir / f'{meta.name}.md'
            out.write_text(page.to_markdown(), encoding='utf-8')
            generated.append(out)
        return generated

    # ------------------------------------------------------------------
    # Workflow documentation
    # ------------------------------------------------------------------

    def generate_workflow_docs(self, recipe_dir: Path) -> list[Path]:
        """Write one Markdown file per YAML workflow recipe in *recipe_dir*.

        Parameters
        ----------
        recipe_dir:
            Directory containing ``*.yaml`` workflow recipes.

        Returns
        -------
        list[Path]
            Paths of the generated files.
        """
        workflows_dir = self.output_dir / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []
        for yaml_file in sorted(recipe_dir.glob('*.yaml')):
            raw = yaml.safe_load(yaml_file.read_text(encoding='utf-8')) or {}
            page = WorkflowDocPage(
                name=raw.get('name', yaml_file.stem),
                version=raw.get('version', '1.0.0'),
                description=raw.get('description', ''),
                steps=raw.get('steps', []),
                tags=raw.get('tags', []),
            )
            out = workflows_dir / f'{yaml_file.stem}.md'
            out.write_text(page.to_markdown(), encoding='utf-8')
            generated.append(out)
        return generated

    # ------------------------------------------------------------------
    # Index
    # ------------------------------------------------------------------

    def generate_index(self, title: str = 'Reference Documentation') -> Path:
        """Write a top-level ``index.md`` listing all generated pages."""
        pages = sorted(self.output_dir.rglob('*.md'))
        lines = [f'# {title}', '']
        for page in pages:
            rel = page.relative_to(self.output_dir)
            lines.append(f'- [{rel}]({rel})')
        out = self.output_dir / 'index.md'
        out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return out
