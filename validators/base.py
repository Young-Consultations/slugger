"""Validator abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationError:
    field: str
    message: str


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)


class BaseValidator(ABC):
    @abstractmethod
    def validate(self, target: Any, **kwargs: Any) -> ValidationResult:
        """Validate a target object and return the result."""
