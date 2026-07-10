"""Agent domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(str, Enum):
    """Runtime status for an agent."""

    IDLE = 'idle'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    DISABLED = 'disabled'


@dataclass(slots=True, frozen=True)
class AgentCapability:
    """Describes a discrete unit of agent functionality."""

    name: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()


@dataclass(slots=True)
class AgentMetadata:
    """Standard metadata exposed by every agent."""

    name: str
    version: str
    description: str
    category: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    provider: str | None = None
    external_interface: str | None = None
