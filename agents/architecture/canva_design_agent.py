"""Canva design workflow agent with artifact ingestion.

Bridges the Canva design service with the agent framework, allowing
design artifacts to be produced and ingested as part of a standard
workflow.
"""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DiagramArtifact, DocumentArtifact
from models.execution import ExecutionContext
from services.canva.base import ICanvaService
from services.canva.models import CanvaExportFormat


class CanvaDesignAgent(BaseAgent):
    """Produce design artifacts by exporting Canva designs.

    The agent accepts an optional ``design_id`` from the execution
    context metadata.  If no ID is supplied it lists available designs
    and uses the first match for the project name or the first design
    in the library.

    The exported design URL is wrapped in a :class:`DiagramArtifact` so
    it can flow through the standard workflow artifact chain.
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

        if design_id:
            design = self._canva.get_design(design_id)
        else:
            designs = self._canva.list_designs()
            if not designs:
                # No designs available — produce a placeholder artifact
                artifact = self.create_artifact(
                    context,
                    'design_artifact',
                    '# Design Artifact\n\nNo Canva designs are currently available.',
                    DocumentArtifact,
                )
                return [artifact]
            design = designs[0]

        job = self._canva.export_design(design.design_id, export_format)
        export_url = job.urls[0] if job.urls else ''

        content = (
            f'# Canva Design Export\n\n'
            f'**Design:** {design.title}\n'
            f'**Design ID:** {design.design_id}\n'
            f'**Export Format:** {export_format.value.upper()}\n'
            f'**Export URL:** {export_url}\n'
            f'**Job ID:** {job.job_id}\n'
            f'**Status:** {job.status}\n'
        )
        artifact = self.create_artifact(context, 'design_artifact', content, DiagramArtifact)
        artifact.format = export_format.value
        return [artifact]
