"""Base agent implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type
from uuid import uuid4

from core.exceptions import AgentError
from core.interfaces import IAgent, IObserver
from models.agent import AgentCapability, AgentMetadata, AgentStatus
from models.artifact import Artifact, ArtifactMetadata, DocumentArtifact
from models.execution import ExecutionContext, ExecutionEvent, ExecutionState
from observability.models import Event


class BaseAgent(IAgent, ABC):
    """Common lifecycle logic for all concrete agents."""

    def __init__(self, metadata: AgentMetadata, capabilities: list[AgentCapability], observer: IObserver | None = None) -> None:
        self._metadata = metadata
        self._capabilities = capabilities
        self._status = AgentStatus.IDLE
        self._observer = observer

    @property
    def metadata(self) -> AgentMetadata:
        return self._metadata

    @property
    def capabilities(self) -> list[AgentCapability]:
        return self._capabilities

    @property
    def status(self) -> AgentStatus:
        return self._status

    def execute(self, context: ExecutionContext) -> list[Artifact]:
        self._status = AgentStatus.RUNNING
        context.state = ExecutionState.RUNNING
        self._emit('agent.execute.started', context)
        self.on_before_execute(context)
        try:
            self.validate_inputs(context)
            artifacts = self._execute(context)
            self.validate_outputs(artifacts)
            self.on_after_execute(context, artifacts)
        except Exception as error:
            self._status = AgentStatus.FAILED
            context.state = ExecutionState.FAILED
            self._emit('agent.execute.failed', context, error=str(error))
            raise AgentError(str(error)) from error
        self._status = AgentStatus.SUCCEEDED
        context.state = ExecutionState.SUCCEEDED
        self._emit('agent.execute.completed', context, artifacts=len(artifacts))
        return artifacts

    def validate_inputs(self, context: ExecutionContext) -> None:
        missing = [name for name in self.metadata.inputs if name not in context.inputs]
        if missing:
            raise AgentError(f'Missing required inputs for {self.metadata.name}: {", ".join(missing)}')

    def validate_outputs(self, artifacts: list[Artifact]) -> None:
        if not artifacts:
            raise AgentError(f'Agent {self.metadata.name} produced no artifacts.')

    def on_before_execute(self, context: ExecutionContext) -> None:
        """Hook called before execution."""

    def on_after_execute(self, context: ExecutionContext, artifacts: list[Artifact]) -> None:
        """Hook called after successful execution."""

    def create_artifact(self, context: ExecutionContext, name: str, content: str, artifact_class: Type[Artifact] = DocumentArtifact, *, format: str | None = None) -> Artifact:
        artifact = artifact_class(
            artifact_id=str(uuid4()),
            name=name,
            content=content,
            metadata=ArtifactMetadata(source_agent=self.metadata.name, source_step=context.step_name, project_id=context.project_id, correlation_id=context.correlation_id),
        )
        if format is not None:
            artifact.format = format
        return artifact

    def _emit(self, name: str, context: ExecutionContext, **payload: object) -> None:
        context.add_event(ExecutionEvent(name=name, payload={'agent': self.metadata.name, **payload}))
        if self._observer is not None:
            self._observer.emit(Event(name=name, payload={'agent': self.metadata.name, **payload}))

    @abstractmethod
    def _execute(self, context: ExecutionContext) -> list[Artifact]:
        """Perform concrete agent work."""
