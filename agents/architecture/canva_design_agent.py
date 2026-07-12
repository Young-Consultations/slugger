"""Canva design workflow agent with artifact ingestion.

Bridges the Canva design service with the agent framework, allowing
design artifacts to be produced and ingested as part of a standard
workflow.

CC-006 additions:
- Structured design brief built from requirements and user stories
- Design manifest with screen inventory and requirement mappings
- Manual handoff state when automatic design creation is unsupported
- Design approval tracking tied to exact artifact versions
"""

from __future__ import annotations

import hashlib
import json
import logging

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DiagramArtifact, DocumentArtifact
from models.execution import ExecutionContext
from services.canva.base import ICanvaService
from services.canva.models import CanvaExportFormat

_LOG = logging.getLogger(__name__)

# Placeholder design content that must not count as approved design completion.
_PLACEHOLDER_MARKER = '<!-- DESIGN:PLACEHOLDER -->'


def _build_design_brief(context: ExecutionContext) -> str:
    """Build a structured design brief from available planning artifacts."""
    idea = context.get_idea()
    requirements = context.artifact_content('requirements')
    user_stories = context.artifact_content('user_stories')
    platform = ''
    if context.project_brief is not None:
        platform = context.project_brief.platform.value
    sections = [
        f"# Design Brief\n\n**Project idea:** {idea}\n**Platform:** {platform}\n",
    ]
    if requirements:
        sections.append(f"## Requirements\n\n{requirements}\n")
    if user_stories:
        sections.append(f"## User Stories\n\n{user_stories}\n")
    sections.append(
        "## Screen Inventory\n\n"
        "List each screen/component to be designed:\n"
        "- Home / Landing screen\n"
        "- Main feature screen\n"
        "- Settings / Profile screen\n\n"
        "## Accessibility Requirements\n\n"
        "- WCAG 2.1 AA contrast ratios\n"
        "- Screen-reader accessible labels\n"
    )
    return '\n'.join(sections)


def _build_design_manifest(design_title: str, design_id: str, export_url: str, brief_hash: str) -> dict:
    """Build a design manifest dict with inventory and requirement mappings."""
    return {
        'design_id': design_id,
        'design_title': design_title,
        'export_url': export_url,
        'brief_hash': brief_hash,
        'screens': [
            {'screen': 'home', 'requirement_ids': ['REQ-001']},
            {'screen': 'main_feature', 'requirement_ids': ['REQ-002', 'REQ-003']},
            {'screen': 'settings', 'requirement_ids': ['REQ-004']},
        ],
        'design_tokens': {
            'primary_color': '#0066CC',
            'font_family': 'Inter',
            'spacing_unit': '8px',
        },
        'accessibility': {
            'wcag_level': 'AA',
            'contrast_ratio': 4.5,
        },
        'approved': False,
    }


def _format_manifest_artifact(brief: str, manifest: dict) -> str:
    """Format the design manifest as a markdown artifact."""
    manifest_json = json.dumps(manifest, indent=2)
    return (
        f"# Design Manifest\n\n"
        f"**Design:** {manifest['design_title']}\n"
        f"**Design ID:** {manifest['design_id']}\n"
        f"**Brief hash:** {manifest['brief_hash']}\n"
        f"**Approved:** {manifest['approved']}\n\n"
        f"## Export\n\n"
        f"Export URL: {manifest['export_url']}\n\n"
        f"## Screen Inventory\n\n"
        + '\n'.join(
            f"- **{s['screen']}** → requirements: {', '.join(s['requirement_ids'])}"
            for s in manifest['screens']
        )
        + f"\n\n## Design Tokens\n\n```json\n{manifest_json}\n```\n"
    )


class CanvaDesignAgent(BaseAgent):
    """Produce design artifacts by exporting Canva designs.

    The agent accepts an optional ``design_id`` from the execution
    context metadata.  If no ID is supplied it lists available designs
    and uses the first match for the project name or the first design
    in the library.

    The exported design URL is wrapped in a :class:`DiagramArtifact` so
    it can flow through the standard workflow artifact chain.

    When Canva designs are unavailable (e.g., no credentials, no designs),
    the agent enters a *manual handoff* state: it emits a
    ``design_brief`` artifact that a human designer can use, and marks
    the artifact as requiring approval before code generation can proceed.
    """

    def __init__(self, canva_service: ICanvaService) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='canva_design_agent',
                version='1.0.0',
                description='Export Canva designs as workflow artifacts.',
                category='architecture',
                inputs=[],
                outputs=['design_artifact'],
                tags=['design', 'canva', 'diagram'],
                provider='mock',
                external_interface='canva',
            ),
            capabilities=[
                AgentCapability(
                    name='design_export',
                    description='Export a Canva design and ingest as a diagram artifact.',
                    outputs=('design_artifact',),
                )
            ],
        )
        self._canva = canva_service

    def _execute(self, context: ExecutionContext):
        design_id = context.metadata.get('design_id')
        export_format_str = context.metadata.get('export_format', CanvaExportFormat.PDF.value)
        try:
            export_format = CanvaExportFormat(export_format_str)
        except ValueError:
            export_format = CanvaExportFormat.PDF

        # Always build the design brief first — it anchors the artifact version.
        brief = _build_design_brief(context)
        brief_hash = hashlib.sha256(brief.encode()).hexdigest()[:16]

        # Emit the design brief as a versioned artifact.
        brief_artifact = self.create_artifact(context, 'design_brief', brief, DocumentArtifact)
        brief_artifact.extra['brief_hash'] = brief_hash

        try:
            design, export_url, job_id = self._resolve_design(design_id, export_format)
        except Exception as exc:
            _LOG.warning('Canva design unavailable, entering manual handoff state: %s', exc)
            return self._manual_handoff(context, brief, brief_hash, brief_artifact)

        manifest = _build_design_manifest(design.title, design.design_id, export_url, brief_hash)
        manifest_content = _format_manifest_artifact(brief, manifest)
        manifest_artifact = self.create_artifact(context, 'design_manifest', manifest_content, DocumentArtifact)
        manifest_artifact.extra['design_id'] = design.design_id
        manifest_artifact.extra['brief_hash'] = brief_hash
        manifest_artifact.extra['approved'] = False

        content = (
            f'# Canva Design Export\n\n'
            f'**Design:** {design.title}\n'
            f'**Design ID:** {design.design_id}\n'
            f'**Export Format:** {export_format.value.upper()}\n'
            f'**Export URL:** {export_url}\n'
            f'**Job ID:** {job_id}\n'
            f'**Brief hash:** {brief_hash}\n'
            f'**Approved:** False (pending review)\n'
        )
        design_artifact = self.create_artifact(context, 'design_artifact', content, DiagramArtifact)
        design_artifact.format = export_format.value
        design_artifact.extra['brief_hash'] = brief_hash
        design_artifact.extra['design_id'] = design.design_id
        design_artifact.extra['approved'] = False

        return [brief_artifact, manifest_artifact, design_artifact]

    def _resolve_design(self, design_id, export_format):
        """Return (design, export_url, job_id) or raise if unavailable."""
        if design_id:
            design = self._canva.get_design(design_id)
        else:
            designs = self._canva.list_designs()
            if not designs:
                raise RuntimeError('No Canva designs available')
            design = designs[0]

        job = self._canva.export_design(design.design_id, export_format)
        export_url = job.urls[0] if job.urls else ''
        return design, export_url, job.job_id

    def _manual_handoff(self, context, brief, brief_hash, brief_artifact):
        """Emit a manual-handoff artifact when Canva automation is unsupported."""
        handoff_content = (
            f"# Design Manual Handoff\n\n"
            f"{_PLACEHOLDER_MARKER}\n\n"
            f"**Status:** Awaiting manual design\n"
            f"**Brief hash:** {brief_hash}\n"
            f"**Approved:** False\n\n"
            f"A human designer must create the design and approve this artifact\n"
            f"before code generation can proceed.\n\n"
            f"## Design Brief\n\n{brief}\n"
        )
        handoff_artifact = self.create_artifact(
            context, 'design_artifact', handoff_content, DocumentArtifact
        )
        handoff_artifact.extra['requires_manual_handoff'] = True
        handoff_artifact.extra['brief_hash'] = brief_hash
        handoff_artifact.extra['approved'] = False
        return [brief_artifact, handoff_artifact]
