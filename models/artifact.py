"""Artifact domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ArtifactType(str, Enum):
    """Supported artifact categories."""

    DOCUMENT = 'document'
    CODE = 'code'
    TEST = 'test'
    CONFIG = 'config'
    DIAGRAM = 'diagram'
    REPORT = 'report'


class ArtifactStatus(str, Enum):
    """Lifecycle status for an artifact."""

    DRAFT = 'draft'
    READY = 'ready'
    VALIDATED = 'validated'
    REJECTED = 'rejected'
    ARCHIVED = 'archived'


@dataclass(slots=True)
class ArtifactMetadata:
    """Traceability metadata stored on every artifact."""

    source_agent: str = 'unknown'
    source_step: str = 'unknown'
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = '1.0.0'
    project_id: str | None = None
    correlation_id: str | None = None
    labels: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Artifact:
    """Base artifact exchanged between agents."""

    artifact_id: str
    name: str
    artifact_type: ArtifactType
    content: str
    status: ArtifactStatus = ArtifactStatus.DRAFT
    metadata: ArtifactMetadata = field(default_factory=ArtifactMetadata)
    format: str = 'markdown'
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentArtifact(Artifact):
    """Structured document artifact."""

    artifact_type: ArtifactType = field(default=ArtifactType.DOCUMENT, init=False)


@dataclass(slots=True)
class CodeArtifact(Artifact):
    """Source code or implementation artifact."""

    artifact_type: ArtifactType = field(default=ArtifactType.CODE, init=False)
    format: str = 'python'


@dataclass(slots=True)
class TestArtifact(Artifact):
    """Test specification or test result artifact."""

    artifact_type: ArtifactType = field(default=ArtifactType.TEST, init=False)
    format: str = 'text'


@dataclass(slots=True)
class ConfigArtifact(Artifact):
    """Configuration or infrastructure artifact."""

    artifact_type: ArtifactType = field(default=ArtifactType.CONFIG, init=False)
    format: str = 'yaml'


@dataclass(slots=True)
class DiagramArtifact(Artifact):
    """Diagram or visualization artifact."""

    artifact_type: ArtifactType = field(default=ArtifactType.DIAGRAM, init=False)
    format: str = 'mermaid'
