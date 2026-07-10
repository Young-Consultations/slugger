"""ProductVisionAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import DocumentArtifact
from models.execution import ExecutionContext


class ProductVisionAgent(BaseAgent):
    """Create product vision artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='product_vision_agent',
                version='1.0.0',
                description='Create product vision artifacts.',
                category='planning',
                inputs=[],
                outputs=['product_vision'],
                tags=['planning', 'product_vision'],
                provider='mock',
            ),
            capabilities=[AgentCapability(name='product_vision', description='Create product vision artifacts.', outputs=('product_vision',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Product Vision\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'product_vision', content, DocumentArtifact)]
