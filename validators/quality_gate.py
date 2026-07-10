"""Quality gate evaluator."""

from __future__ import annotations

from typing import Any

from models.workflow import QualityGate
from validators.base import BaseValidator, ValidationResult


class QualityGateEvaluator:
    def __init__(self, validators: dict[str, BaseValidator]) -> None:
        self.validators = validators

    def evaluate(self, gates: list[QualityGate], target: Any) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        for gate in gates:
            results.append(self.validators[gate.validator].validate(target, **gate.config))
        return results
