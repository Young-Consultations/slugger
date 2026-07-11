"""Workflow state persistence for resumable execution."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from models.workflow import StepStatus
from workflow.models import StepInstance, WorkflowDefinition, WorkflowInstance, WorkflowStepDefinition


def _new_run_id() -> str:
    return str(uuid4())


def _serialize_instance(instance: WorkflowInstance) -> dict:
    """Convert a :class:`WorkflowInstance` to a JSON-serialisable dict.

    Only the fields needed to reconstruct progress are stored (definition
    structure, per-step status and attempts).  Artifact *content* is not
    persisted here; callers may use a separate artifact store for that.
    """
    return {
        'run_id': instance.run_id,
        'status': instance.status,
        'definition': {
            'name': instance.definition.name,
            'version': instance.definition.version,
            'description': instance.definition.description,
            'tags': instance.definition.tags,
            'steps': [
                {
                    'name': s.name,
                    'agent': s.agent,
                    'description': s.description,
                    'inputs': s.inputs,
                    'outputs': s.outputs,
                    'quality_gates': [asdict(qg) for qg in s.quality_gates],
                    'retry_policy': s.retry_policy,
                    'on_failure': s.on_failure,
                    'metadata': s.metadata,
                }
                for s in instance.definition.steps
            ],
        },
        'step_instances': [
            {'name': si.definition.name, 'status': si.status.value, 'attempts': si.attempts}
            for si in instance.step_instances
        ],
    }


def _deserialize_definition(raw: dict) -> WorkflowDefinition:
    from models.workflow import QualityGate
    steps = []
    for s in raw.get('steps', []):
        gates = [QualityGate(**qg) for qg in s.get('quality_gates', [])]
        steps.append(WorkflowStepDefinition(
            name=s['name'],
            agent=s['agent'],
            description=s.get('description', ''),
            inputs=s.get('inputs', []),
            outputs=s.get('outputs', []),
            quality_gates=gates,
            retry_policy=s.get('retry_policy', {}),
            on_failure=s.get('on_failure', 'stop'),
            metadata=s.get('metadata', {}),
        ))
    return WorkflowDefinition(
        name=raw['name'],
        version=raw['version'],
        description=raw.get('description', ''),
        steps=steps,
        tags=raw.get('tags', []),
    )


def _deserialize_instance(payload: dict) -> WorkflowInstance:
    definition = _deserialize_definition(payload['definition'])
    step_map = {si['name']: si for si in payload.get('step_instances', [])}
    step_instances = []
    for step_def in definition.steps:
        raw_si = step_map.get(step_def.name, {})
        si = StepInstance(
            definition=step_def,
            status=StepStatus(raw_si.get('status', StepStatus.PENDING.value)),
            attempts=raw_si.get('attempts', 0),
        )
        step_instances.append(si)
    return WorkflowInstance(
        definition=definition,
        step_instances=step_instances,
        status=payload.get('status', 'pending'),
        run_id=payload.get('run_id', _new_run_id()),
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
            self.path.write_text('{}', encoding='utf-8')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, instance: WorkflowInstance) -> None:
        """Persist the current state of *instance*."""
        store = self._load_store()
        store[instance.run_id] = _serialize_instance(instance)
        self.path.write_text(json.dumps(store, indent=2), encoding='utf-8')

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
        return json.loads(self.path.read_text(encoding='utf-8'))
