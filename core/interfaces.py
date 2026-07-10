"""Core interfaces used across Slugger."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models.agent import AgentCapability, AgentMetadata, AgentStatus
from models.artifact import Artifact
from models.execution import ExecutionContext


class IAgent(ABC):
    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """Return agent metadata."""

    @property
    @abstractmethod
    def capabilities(self) -> list[AgentCapability]:
        """Return supported capabilities."""

    @property
    @abstractmethod
    def status(self) -> AgentStatus:
        """Return current agent status."""

    @abstractmethod
    def execute(self, context: ExecutionContext) -> list[Artifact]:
        """Execute the agent and return artifacts."""

    @abstractmethod
    def validate_inputs(self, context: ExecutionContext) -> None:
        """Validate inbound context before execution."""

    @abstractmethod
    def validate_outputs(self, artifacts: list[Artifact]) -> None:
        """Validate output artifacts after execution."""


class IWorkflowEngine(ABC):
    @abstractmethod
    def run(self, workflow_name: str, **kwargs: Any) -> Any:
        """Run a workflow by name."""

    @abstractmethod
    def list_workflows(self) -> list[str]:
        """List available workflow definitions."""


class IMemorySystem(ABC):
    @abstractmethod
    def store(self, key: str, value: Any, **kwargs: Any) -> Any:
        """Store a memory entry."""

    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> Any:
        """Search memory."""

    @abstractmethod
    def retrieve(self, key: str, **kwargs: Any) -> Any:
        """Retrieve a memory entry."""

    @abstractmethod
    def forget(self, key: str, **kwargs: Any) -> None:
        """Delete a memory entry."""


class IArtifactStore(ABC):
    @abstractmethod
    def create(self, artifact: Artifact) -> Artifact:
        """Persist an artifact."""

    @abstractmethod
    def get(self, artifact_id: str) -> Artifact | None:
        """Retrieve an artifact by id."""

    @abstractmethod
    def list(self) -> list[Artifact]:
        """List stored artifacts."""

    @abstractmethod
    def delete(self, artifact_id: str) -> None:
        """Delete an artifact."""


class IPlugin(ABC):
    @abstractmethod
    def load(self) -> None:
        """Load the plugin."""

    @abstractmethod
    def unload(self) -> None:
        """Unload the plugin."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return plugin health."""


class IValidator(ABC):
    @abstractmethod
    def validate(self, target: Any, **kwargs: Any) -> Any:
        """Validate a target object."""


class IObserver(ABC):
    @abstractmethod
    def emit(self, event: Any) -> None:
        """Emit an event to the observer."""
