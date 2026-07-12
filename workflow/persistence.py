"""Workflow state persistence for resumable execution."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from models.artifact import (
    Artifact,
    ArtifactMetadata,
    ArtifactStatus,
    ArtifactType,
    DocumentArtifact,
    CodeArtifact,
    TestArtifact,
    ConfigArtifact,
    DiagramArtifact,
)
from models.workflow import StepStatus
from workflow.models import (
    StepInstance,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStepDefinition,
)

_ARTIFACT_CLASSES: dict[str, type[Artifact]] = {
    ArtifactType.DOCUMENT.value: DocumentArtifact,
    ArtifactType.CODE.value: CodeArtifact,
    ArtifactType.TEST.value: TestArtifact,
    ArtifactType.CONFIG.value: ConfigArtifact,
    ArtifactType.DIAGRAM.value: DiagramArtifact,
}


def _new_run_id() -> str:
    return str(uuid4())


def _serialize_artifact(artifact: Artifact) -> dict:
    """Serialise *artifact* to a JSON-compatible dict.

    Schema::

        {
          "artifact_id": str,
          "name": str,
          "artifact_type": str (ArtifactType value),
          "content": str,
          "status": str (ArtifactStatus value),
          "format": str,
          "tags": list[str],
          "metadata": {
            "source_agent": str,
            "source_step": str,
            "version": str,
            "project_id": str | None,
            "correlation_id": str | None,
            "labels": dict[str, str],
            "created_at": str (ISO-8601),
          }
        }
    """
    return {
        "artifact_id": artifact.artifact_id,
        "name": artifact.name,
        "artifact_type": artifact.artifact_type.value,
        "content": artifact.content,
        "status": artifact.status.value,
        "format": artifact.format,
        "tags": artifact.tags,
        "metadata": {
            "source_agent": artifact.metadata.source_agent,
            "source_step": artifact.metadata.source_step,
            "version": artifact.metadata.version,
            "project_id": artifact.metadata.project_id,
            "correlation_id": artifact.metadata.correlation_id,
            "labels": artifact.metadata.labels,
            "created_at": artifact.metadata.created_at.isoformat(),
        },
    }


def _deserialize_artifact(raw: dict) -> Artifact:
    """Reconstruct an :class:`Artifact` subclass from a serialised *raw* dict.

    The ``artifact_type`` field is used to select the appropriate subclass via
    :data:`_ARTIFACT_CLASSES`.  Unknown types fall back to
    :class:`~models.artifact.DocumentArtifact`.
    """
    meta_raw = raw.get("metadata", {})
    raw_ts = meta_raw.get("created_at")
    created_at = (
        datetime.fromisoformat(raw_ts) if raw_ts else datetime.now(timezone.utc)
    )
    metadata = ArtifactMetadata(
        source_agent=meta_raw.get("source_agent", "unknown"),
        source_step=meta_raw.get("source_step", "unknown"),
        version=meta_raw.get("version", "1.0.0"),
        project_id=meta_raw.get("project_id"),
        correlation_id=meta_raw.get("correlation_id"),
        labels=meta_raw.get("labels", {}),
        created_at=created_at,
    )
    artifact_type = raw.get("artifact_type", ArtifactType.DOCUMENT.value)
    cls = _ARTIFACT_CLASSES.get(artifact_type, DocumentArtifact)
    return cls(  # type: ignore[call-arg]
        artifact_id=raw["artifact_id"],
        name=raw["name"],
        content=raw["content"],
        status=ArtifactStatus(raw.get("status", ArtifactStatus.DRAFT.value)),
        format=raw.get("format", "markdown"),
        tags=raw.get("tags", []),
        metadata=metadata,
    )


def _serialize_instance(instance: WorkflowInstance) -> dict:
    """Convert a :class:`WorkflowInstance` to a JSON-serialisable dict."""
    return {
        "run_id": instance.run_id,
        "status": instance.status,
        "definition": {
            "name": instance.definition.name,
            "version": instance.definition.version,
            "description": instance.definition.description,
            "tags": instance.definition.tags,
            "steps": [
                {
                    "name": s.name,
                    "agent": s.agent,
                    "description": s.description,
                    "inputs": s.inputs,
                    "outputs": s.outputs,
                    "quality_gates": [asdict(qg) for qg in s.quality_gates],
                    "retry_policy": s.retry_policy,
                    "on_failure": s.on_failure,
                    "metadata": s.metadata,
                }
                for s in instance.definition.steps
            ],
        },
        "step_instances": [
            {
                "name": si.definition.name,
                "status": si.status.value,
                "attempts": si.attempts,
                "artifacts": [_serialize_artifact(a) for a in si.artifacts],
            }
            for si in instance.step_instances
        ],
        "artifacts": [_serialize_artifact(a) for a in instance.artifacts],
    }


def _deserialize_definition(raw: dict) -> WorkflowDefinition:
    from models.workflow import QualityGate

    steps = []
    for s in raw.get("steps", []):
        gates = [QualityGate(**qg) for qg in s.get("quality_gates", [])]
        steps.append(
            WorkflowStepDefinition(
                name=s["name"],
                agent=s["agent"],
                description=s.get("description", ""),
                inputs=s.get("inputs", []),
                outputs=s.get("outputs", []),
                quality_gates=gates,
                retry_policy=s.get("retry_policy", {}),
                on_failure=s.get("on_failure", "stop"),
                metadata=s.get("metadata", {}),
            )
        )
    return WorkflowDefinition(
        name=raw["name"],
        version=raw["version"],
        description=raw.get("description", ""),
        steps=steps,
        tags=raw.get("tags", []),
    )


def _deserialize_instance(payload: dict) -> WorkflowInstance:
    definition = _deserialize_definition(payload["definition"])
    step_map = {si["name"]: si for si in payload.get("step_instances", [])}
    step_instances = []
    for step_def in definition.steps:
        raw_si = step_map.get(step_def.name, {})
        si = StepInstance(
            definition=step_def,
            status=StepStatus(raw_si.get("status", StepStatus.PENDING.value)),
            attempts=raw_si.get("attempts", 0),
            artifacts=[_deserialize_artifact(a) for a in raw_si.get("artifacts", [])],
        )
        step_instances.append(si)
    instance_artifacts = [
        _deserialize_artifact(a) for a in payload.get("artifacts", [])
    ]
    return WorkflowInstance(
        definition=definition,
        step_instances=step_instances,
        artifacts=instance_artifacts,
        status=payload.get("status", "pending"),
        run_id=payload.get("run_id", _new_run_id()),
    )


class WorkflowPersistence:
    """Save and load :class:`WorkflowInstance` state to/from a JSON file.

    Each run is keyed by its ``run_id`` inside the JSON store.

    Parameters
    ----------
    path:
        Path to the JSON state file.  The parent directory is created
        automatically if it does not already exist.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, instance: WorkflowInstance) -> None:
        """Persist the current state of *instance*."""
        store = self._load_store()
        store[instance.run_id] = _serialize_instance(instance)
        self.path.write_text(json.dumps(store, indent=2), encoding="utf-8")

    def load(self, run_id: str) -> WorkflowInstance | None:
        """Return the saved :class:`WorkflowInstance` for *run_id*, or ``None``."""
        store = self._load_store()
        raw = store.get(run_id)
        if raw is None:
            return None
        return _deserialize_instance(raw)

    def list_runs(self) -> list[str]:
        """Return all stored run IDs."""
        return list(self._load_store().keys())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_store(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))
