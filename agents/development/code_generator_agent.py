"""CodeGeneratorAgent implementation."""

from __future__ import annotations

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import CodeArtifact
from models.execution import ExecutionContext


class CodeGeneratorAgent(BaseAgent):
    """Create code artifacts."""

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='code_generator_agent',
                version='1.0.0',
                description='Create code artifacts.',
                category='development',
                inputs=[],
                outputs=['generated_code'],
                tags=['development', 'code_generation'],
                provider='mock',
                external_interface='openai_codex',
            ),
            capabilities=[AgentCapability(name='code_generation', description='Create code artifacts.', outputs=('generated_code',))],
        )

    def _execute(self, context: ExecutionContext):
        summary = context.inputs or {'note': 'No explicit inputs were supplied.'}
        content = f"# Generated Code\n\nAgent: {self.metadata.name}\n\nContext: {summary}"
        return [self.create_artifact(context, 'generated_code', content, CodeArtifact)]
