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


class ArtifactSchemaValidator(BaseValidator):
    """Validate artifact content against its typed SDLC schema (CC-002).

    Uses :data:`prompts.catalog.ARTIFACT_SCHEMAS` to check that required
    section headers are present in the artifact content.
    """

    def validate(self, target: Artifact, **kwargs: object) -> ValidationResult:
        from prompts.catalog import ARTIFACT_SCHEMAS
        errors: list[ValidationError] = []
        schema = ARTIFACT_SCHEMAS.get(target.name)
        if schema is not None:
            schema_errors = schema.validate(target.content)
            for msg in schema_errors:
                errors.append(ValidationError(field='content', message=msg))
        return ValidationResult(valid=not errors, errors=errors)
