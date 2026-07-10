"""Artifact validator."""

from __future__ import annotations

from models.artifact import Artifact
from validators.base import BaseValidator, ValidationError, ValidationResult


class ArtifactValidator(BaseValidator):
    def validate(self, target: Artifact, **kwargs: object) -> ValidationResult:
        errors: list[ValidationError] = []
        require_content = bool(kwargs.get('require_content', True))
        if not target.artifact_id:
            errors.append(ValidationError(field='artifact_id', message='Artifact id is required.'))
        if not target.name:
            errors.append(ValidationError(field='name', message='Artifact name is required.'))
        if require_content and not target.content.strip():
            errors.append(ValidationError(field='content', message='Artifact content is required.'))
        return ValidationResult(valid=not errors, errors=errors)
