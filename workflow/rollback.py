"""Rollback guidance — generate and store step-level rollback instructions.

:class:`RollbackGuidance` pairs each workflow step with a human-readable
(or script-based) rollback recipe so that operators can safely undo partial
runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RollbackStep:
    """A single rollback instruction for one workflow step.

    Parameters
    ----------
    step_name:
        The workflow step this guidance applies to.
    description:
        Human-readable description of what the rollback does.
    commands:
        Optional ordered list of shell commands to execute.
    metadata:
        Arbitrary annotations (e.g. ``{'author': 'ci-agent'}``).
    """

    step_name: str
    description: str
    commands: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_name": self.step_name,
            "description": self.description,
            "commands": self.commands,
            "metadata": self.metadata,
        }


class RollbackGuidance:
    """Container for rollback instructions spanning an entire workflow run.

    Guidance is registered per workflow step and can be retrieved
    individually or as an ordered list.

    Examples
    --------
    >>> guidance = RollbackGuidance(run_id='abc')
    >>> guidance.register(RollbackStep('deploy', 'Delete the deployed resources',
    ...                                commands=['kubectl delete -f manifests/']))
    >>> guidance.for_step('deploy').description
    'Delete the deployed resources'
    """

    def __init__(self, run_id: str = "") -> None:
        self.run_id = run_id
        self._steps: dict[str, RollbackStep] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, step: RollbackStep) -> None:
        """Register *step* guidance.  Overwrites any previous guidance for the same step."""
        self._steps[step.step_name] = step

    def register_simple(
        self, step_name: str, description: str, commands: list[str] | None = None
    ) -> RollbackStep:
        """Convenience helper — build and register a :class:`RollbackStep`.

        Returns the created step.
        """
        rollback = RollbackStep(
            step_name=step_name,
            description=description,
            commands=commands or [],
        )
        self.register(rollback)
        return rollback

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def for_step(self, step_name: str) -> RollbackStep | None:
        """Return rollback guidance for *step_name*, or ``None``."""
        return self._steps.get(step_name)

    def all_steps(self) -> list[RollbackStep]:
        """Return all rollback steps in registration order."""
        return list(self._steps.values())

    def to_dict(self) -> dict[str, Any]:
        """Serialise the full guidance to a JSON-compatible dict."""
        return {
            "run_id": self.run_id,
            "steps": [s.to_dict() for s in self._steps.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RollbackGuidance":
        """Reconstruct guidance from a serialised dict."""
        guidance = cls(run_id=data.get("run_id", ""))
        for raw in data.get("steps", []):
            guidance.register(
                RollbackStep(
                    step_name=raw["step_name"],
                    description=raw["description"],
                    commands=raw.get("commands", []),
                    metadata=raw.get("metadata", {}),
                )
            )
        return guidance
