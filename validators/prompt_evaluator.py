"""Prompt template evaluator for regression testing and quality gates."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from validators.base import BaseValidator, ValidationError, ValidationResult

_PLACEHOLDER_RE = re.compile(r'\{\{\s*(\w+)\s*\}\}')


@dataclass(slots=True)
class PromptEvaluationResult:
    """Result produced by :class:`PromptEvaluator` for a single template."""

    template_name: str
    rendered: str
    placeholders_found: list[str]
    missing_variables: list[str]
    validation: ValidationResult


def _extract_placeholders(text: str) -> list[str]:
    """Return the unique placeholder names found in *text*, preserving order."""
    # dict.fromkeys() deduplicates while maintaining insertion order (Python 3.7+).
    return list(dict.fromkeys(_PLACEHOLDER_RE.findall(text)))


def _render(template: str, variables: dict[str, str]) -> str:
    """Substitute ``{{ key }}`` markers in *template* with values from *variables*."""

    def _replace(match: re.Match) -> str:
        return variables.get(match.group(1), match.group(0))

    return _PLACEHOLDER_RE.sub(_replace, template)


class PromptTemplateValidator(BaseValidator):
    """Validate a rendered prompt against a set of quality criteria.

    Parameters
    ----------
    required_sections:
        Substrings that *must* appear in the rendered prompt.
    min_length:
        Minimum character count for the rendered prompt.
    """

    def __init__(
        self,
        required_sections: list[str] | None = None,
        min_length: int = 10,
    ) -> None:
        self.required_sections = required_sections or []
        self.min_length = min_length

    def validate(self, target: str, **kwargs: Any) -> ValidationResult:
        errors: list[ValidationError] = []
        if len(target.strip()) < self.min_length:
            errors.append(ValidationError(
                field='content',
                message=f'Rendered prompt is shorter than minimum length ({self.min_length} chars).',
            ))
        for section in self.required_sections:
            if section not in target:
                errors.append(ValidationError(
                    field='section',
                    message=f'Required section not found in rendered prompt: {section!r}',
                ))
        return ValidationResult(valid=not errors, errors=errors)


class PromptEvaluator:
    """Evaluate prompt templates for completeness and quality.

    Parameters
    ----------
    template_dir:
        Directory containing ``*.md`` prompt template files.
    validator:
        Optional :class:`PromptTemplateValidator` applied to every rendered
        prompt.  A default validator requiring at least 10 characters is used
        when not supplied.
    """

    def __init__(
        self,
        template_dir: Path,
        validator: PromptTemplateValidator | None = None,
    ) -> None:
        self.template_dir = template_dir
        self.validator = validator or PromptTemplateValidator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_templates(self) -> list[str]:
        """Return the stems of all ``*.md`` files in the template directory."""
        return sorted(p.stem for p in self.template_dir.glob('*.md'))

    def load_template(self, name: str) -> str:
        """Return the raw text of the named template."""
        candidates = [
            self.template_dir / name,
            self.template_dir / f'{name}.md',
        ]
        for path in candidates:
            if path.exists():
                return path.read_text(encoding='utf-8')
        raise FileNotFoundError(f'Template not found: {name!r} in {self.template_dir}')

    def extract_placeholders(self, name: str) -> list[str]:
        """Return placeholder names declared in the named template."""
        return _extract_placeholders(self.load_template(name))

    def render(self, name: str, variables: dict[str, str]) -> str:
        """Render the named template using *variables*."""
        return _render(self.load_template(name), variables)

    def evaluate(
        self,
        name: str,
        variables: dict[str, str],
        extra_sections: list[str] | None = None,
    ) -> PromptEvaluationResult:
        """Render *name* with *variables* and run quality validation.

        Parameters
        ----------
        name:
            Template name (with or without ``.md`` extension).
        variables:
            Variable bindings used to fill placeholders.
        extra_sections:
            Additional substrings that must appear in the rendered output,
            supplementing the validator's ``required_sections``.
        """
        template = self.load_template(name)
        placeholders = _extract_placeholders(template)
        missing = [p for p in placeholders if p not in variables]
        rendered = _render(template, variables)

        validator = self.validator
        if extra_sections:
            validator = PromptTemplateValidator(
                required_sections=list(self.validator.required_sections) + extra_sections,
                min_length=self.validator.min_length,
            )
        validation = validator.validate(rendered)
        return PromptEvaluationResult(
            template_name=name,
            rendered=rendered,
            placeholders_found=placeholders,
            missing_variables=missing,
            validation=validation,
        )

    def evaluate_all(self, variables_map: dict[str, dict[str, str]]) -> dict[str, PromptEvaluationResult]:
        """Evaluate every template in *template_dir*.

        Parameters
        ----------
        variables_map:
            Mapping of template stem → variable bindings.  Templates without
            an entry receive an empty binding dict (placeholders remain
            un-substituted).
        """
        results: dict[str, PromptEvaluationResult] = {}
        for stem in self.list_templates():
            variables = variables_map.get(stem, {})
            results[stem] = self.evaluate(stem, variables)
        return results
