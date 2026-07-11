"""Workflow YAML parser."""

from __future__ import annotations

from pathlib import Path

import yaml

from models.workflow import QualityGate
from validators.workflow_validator import WorkflowValidator
from workflow.models import ApprovalPolicy, WorkflowDefinition, WorkflowStepDefinition


class WorkflowParser:
    def __init__(self, validator: WorkflowValidator | None = None) -> None:
        self.validator = validator or WorkflowValidator()

    def parse_file(self, path: Path) -> WorkflowDefinition:
        payload = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        result = self.validator.validate(payload)
        if not result.valid:
            raise ValueError('Invalid workflow definition: ' + ', '.join(error.message for error in result.errors))
        steps = [
            WorkflowStepDefinition(
                name=step['name'],
                agent=step['agent'],
                description=step.get('description', ''),
                inputs=step.get('inputs', []),
                outputs=step.get('outputs', []),
                quality_gates=[QualityGate(validator=gate['validator'], name=gate.get('name'), condition=gate.get('condition'), required=gate.get('required', True), config=gate.get('config', {})) for gate in step.get('quality_gates', [])],
                retry_policy=step.get('retry_policy', {}),
                on_failure=step.get('on_failure', 'stop'),
                approval_policy=ApprovalPolicy.from_dict(step['approval_policy']) if 'approval_policy' in step else None,
                metadata=step.get('metadata', {}),
            )
            for step in payload['steps']
        ]
        return WorkflowDefinition(name=payload['name'], version=payload['version'], description=payload.get('description', ''), steps=steps, tags=payload.get('tags', []), metadata=payload.get('metadata', {}))
