"""Workflow validator."""

from __future__ import annotations

from typing import Any

from validators.base import BaseValidator, ValidationError, ValidationResult


class WorkflowValidator(BaseValidator):
    def validate(self, target: dict[str, Any], **kwargs: object) -> ValidationResult:
        errors: list[ValidationError] = []
        for field in ('name', 'version', 'steps'):
            if field not in target:
                errors.append(ValidationError(field=field, message=f'Missing required field: {field}'))
        steps = target.get('steps', [])
        if not isinstance(steps, list) or not steps:
            errors.append(ValidationError(field='steps', message='Workflow must declare at least one step.'))
        else:
            for index, step in enumerate(steps):
                if 'name' not in step:
                    errors.append(ValidationError(field=f'steps[{index}].name', message='Step name is required.'))
                if 'agent' not in step:
                    errors.append(ValidationError(field=f'steps[{index}].agent', message='Step agent is required.'))
        return ValidationResult(valid=not errors, errors=errors)
