"""Prompt regression suite — detect regressions in prompt template behaviour.

:class:`PromptRegressionSuite` records *baseline* render results for a set of
prompt templates and variables, then compares future renders against those
baselines to detect unexpected changes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from validators.prompt_evaluator import PromptEvaluator


@dataclass
class RegressionBaseline:
    """A stored baseline for one prompt template / variable combination.

    Parameters
    ----------
    template_name:
        Name of the prompt template.
    variables:
        Variables used to render the template.
    rendered_hash:
        SHA-256 digest of the canonical rendered output.
    rendered_length:
        Character length of the rendered output.
    metadata:
        Arbitrary annotations stored alongside the baseline.
    """

    template_name: str
    variables: dict[str, str]
    rendered_hash: str
    rendered_length: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'template_name': self.template_name,
            'variables': self.variables,
            'rendered_hash': self.rendered_hash,
            'rendered_length': self.rendered_length,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RegressionBaseline':
        return cls(
            template_name=data['template_name'],
            variables=data.get('variables', {}),
            rendered_hash=data['rendered_hash'],
            rendered_length=data.get('rendered_length', 0),
            metadata=data.get('metadata', {}),
        )


@dataclass
class RegressionResult:
    """Outcome of comparing a render against its baseline."""

    template_name: str
    passed: bool
    current_hash: str
    baseline_hash: str
    current_length: int
    baseline_length: int
    message: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'template_name': self.template_name,
            'passed': self.passed,
            'current_hash': self.current_hash,
            'baseline_hash': self.baseline_hash,
            'current_length': self.current_length,
            'baseline_length': self.baseline_length,
            'message': self.message,
        }


def _hash_rendered(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _baseline_key(template_name: str, variables: dict[str, str]) -> str:
    serialized_variables = json.dumps(variables, sort_keys=True, separators=(',', ':'))
    return f'{template_name}:{serialized_variables}'


class PromptRegressionSuite:
    """Record baselines and detect prompt regressions.

    Parameters
    ----------
    evaluator:
        A :class:`~validators.prompt_evaluator.PromptEvaluator` used to
        render templates.  If ``None`` a default evaluator is created.
    baseline_path:
        Optional YAML/JSON file to load and persist baselines.
    """

    def __init__(
        self,
        evaluator: PromptEvaluator | None = None,
        baseline_path: Path | None = None,
    ) -> None:
        self._evaluator = evaluator or PromptEvaluator()
        self._baselines: dict[str, RegressionBaseline] = {}
        self._baseline_path = baseline_path
        if baseline_path and baseline_path.exists():
            self._load(baseline_path)

    # ------------------------------------------------------------------
    # Baseline management
    # ------------------------------------------------------------------

    def capture_baseline(
        self,
        template_name: str,
        variables: dict[str, str] | None = None,
    ) -> RegressionBaseline:
        """Render *template_name* and record it as the new baseline.

        Parameters
        ----------
        template_name:
            Key of the template registered on the evaluator.
        variables:
            Substitution variables.  Defaults to an empty dict.

        Returns
        -------
        RegressionBaseline
            The newly recorded baseline.
        """
        variables = variables or {}
        result = self._evaluator.evaluate(template_name, variables)
        rendered = result.rendered
        baseline = RegressionBaseline(
            template_name=template_name,
            variables=variables,
            rendered_hash=_hash_rendered(rendered),
            rendered_length=len(rendered),
        )
        self._baselines[_baseline_key(template_name, variables)] = baseline
        if self._baseline_path:
            self._save(self._baseline_path)
        return baseline

    # ------------------------------------------------------------------
    # Regression detection
    # ------------------------------------------------------------------

    def check(
        self,
        template_name: str,
        variables: dict[str, str] | None = None,
    ) -> RegressionResult:
        """Compare the current render of *template_name* against its baseline.

        Parameters
        ----------
        template_name:
            Template to check.
        variables:
            Variables to use for rendering.

        Returns
        -------
        RegressionResult
            Contains ``passed=True`` when the render matches the baseline.

        Raises
        ------
        KeyError
            If no baseline exists for *template_name*.
        """
        variables = variables or {}
        baseline = self._baselines.get(_baseline_key(template_name, variables))
        if baseline is None:
            raise KeyError(
                f"No baseline recorded for template '{template_name}' "
                f"with variables {variables!r}."
            )

        result = self._evaluator.evaluate(template_name, variables)
        current_hash = _hash_rendered(result.rendered)
        current_len = len(result.rendered)

        passed = current_hash == baseline.rendered_hash
        message = '' if passed else (
            f"Hash mismatch: expected {baseline.rendered_hash[:8]}…, "
            f"got {current_hash[:8]}…"
        )
        return RegressionResult(
            template_name=template_name,
            passed=passed,
            current_hash=current_hash,
            baseline_hash=baseline.rendered_hash,
            current_length=current_len,
            baseline_length=baseline.rendered_length,
            message=message,
        )

    def run_all(self, variables: dict[str, dict[str, str]] | None = None) -> list[RegressionResult]:
        """Run regression checks for all recorded baselines.

        Parameters
        ----------
        variables:
            Mapping of template name → variable dict to use.  Templates not
            present in this mapping use the variables stored in the baseline.

        Returns
        -------
        list[RegressionResult]
        """
        results: list[RegressionResult] = []
        variables = variables or {}
        for baseline in self._baselines.values():
            vars_for_template = variables.get(baseline.template_name, baseline.variables)
            results.append(self.check(baseline.template_name, vars_for_template))
        return results

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [b.to_dict() for b in self._baselines.values()]
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _load(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding='utf-8'))
        for raw in data:
            baseline = RegressionBaseline.from_dict(raw)
            self._baselines[_baseline_key(baseline.template_name, baseline.variables)] = baseline
