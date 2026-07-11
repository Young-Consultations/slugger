"""Agent contracts — formal input/output schema definitions for agents.

A :class:`AgentContract` describes the expected inputs and outputs of an
agent, enabling static validation before execution and serving as
machine-readable documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldSchema:
    """Schema for a single input or output field.

    Parameters
    ----------
    name:
        Artifact or parameter name.
    description:
        Human-readable description of the field.
    required:
        Whether the field must be present.
    field_type:
        Expected Python type name (e.g. ``'str'``, ``'int'``, ``'Artifact'``).
    """

    name: str
    description: str = ''
    required: bool = True
    field_type: str = 'str'


@dataclass
class AgentContract:
    """Formal input/output contract for an agent.

    Parameters
    ----------
    agent_name:
        Canonical agent name (matches :attr:`AgentMetadata.name`).
    inputs:
        Ordered list of input field schemas.
    outputs:
        Ordered list of output artifact schemas.
    version:
        Contract version string (SemVer).
    metadata:
        Arbitrary annotations (e.g. ``{'category': 'planning'}``).
    """

    agent_name: str
    inputs: list[FieldSchema] = field(default_factory=list)
    outputs: list[FieldSchema] = field(default_factory=list)
    version: str = '1.0.0'
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def validate_inputs(self, provided: dict[str, Any]) -> list[str]:
        """Return a list of validation errors for *provided* inputs.

        An error is added for each required input field that is missing from
        *provided*.

        Parameters
        ----------
        provided:
            Mapping of field name → value as supplied by the caller.

        Returns
        -------
        list[str]
            Validation error messages.  Empty list means valid.
        """
        errors: list[str] = []
        for field_schema in self.inputs:
            if field_schema.required and field_schema.name not in provided:
                errors.append(f"Required input '{field_schema.name}' is missing.")
        return errors

    def validate_outputs(self, produced: list[str]) -> list[str]:
        """Return a list of validation errors for *produced* artifact names.

        Parameters
        ----------
        produced:
            Names of artifacts produced by the agent.

        Returns
        -------
        list[str]
            Validation error messages.  Empty list means valid.
        """
        errors: list[str] = []
        for field_schema in self.outputs:
            if field_schema.required and field_schema.name not in produced:
                errors.append(f"Required output '{field_schema.name}' was not produced.")
        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialise the contract to a JSON-compatible dict."""
        return {
            'agent_name': self.agent_name,
            'version': self.version,
            'inputs': [
                {
                    'name': f.name,
                    'description': f.description,
                    'required': f.required,
                    'field_type': f.field_type,
                }
                for f in self.inputs
            ],
            'outputs': [
                {
                    'name': f.name,
                    'description': f.description,
                    'required': f.required,
                    'field_type': f.field_type,
                }
                for f in self.outputs
            ],
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'AgentContract':
        """Deserialise a contract from a plain dict."""

        def _field(raw: dict[str, Any]) -> FieldSchema:
            return FieldSchema(
                name=raw['name'],
                description=raw.get('description', ''),
                required=raw.get('required', True),
                field_type=raw.get('field_type', 'str'),
            )

        return cls(
            agent_name=data['agent_name'],
            inputs=[_field(f) for f in data.get('inputs', [])],
            outputs=[_field(f) for f in data.get('outputs', [])],
            version=data.get('version', '1.0.0'),
            metadata=data.get('metadata', {}),
        )


class ContractRegistry:
    """Registry mapping agent names to their :class:`AgentContract`.

    Contracts can be registered programmatically or loaded from dicts.
    """

    def __init__(self) -> None:
        self._contracts: dict[str, AgentContract] = {}

    def register(self, contract: AgentContract) -> None:
        """Register *contract* for its agent."""
        self._contracts[contract.agent_name] = contract

    def get(self, agent_name: str) -> AgentContract | None:
        """Return the contract for *agent_name*, or ``None``."""
        return self._contracts.get(agent_name)

    def all_contracts(self) -> list[AgentContract]:
        """Return all registered contracts."""
        return list(self._contracts.values())
