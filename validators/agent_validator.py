"""Agent validator."""

from __future__ import annotations

from core.interfaces import IAgent
from validators.base import BaseValidator, ValidationError, ValidationResult


class AgentValidator(BaseValidator):
    def validate(self, target: IAgent, **kwargs: object) -> ValidationResult:
        errors: list[ValidationError] = []
        metadata = target.metadata
        if not metadata.name:
            errors.append(
                ValidationError(field="name", message="Agent name is required.")
            )
        if not metadata.version:
            errors.append(
                ValidationError(field="version", message="Agent version is required.")
            )
        if not target.capabilities:
            errors.append(
                ValidationError(
                    field="capabilities",
                    message="Agent must declare at least one capability.",
                )
            )
        return ValidationResult(valid=not errors, errors=errors)
