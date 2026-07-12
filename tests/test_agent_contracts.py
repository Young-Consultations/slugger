"""Tests for TASK-042: Agent Contracts."""

from __future__ import annotations

from core.contracts import AgentContract, ContractRegistry, FieldSchema


def _make_contract() -> AgentContract:
    return AgentContract(
        agent_name="code_generator_agent",
        inputs=[
            FieldSchema(
                name="requirements", description="Requirements document", required=True
            ),
            FieldSchema(name="architecture", required=False),
        ],
        outputs=[
            FieldSchema(
                name="source_code", description="Generated source", required=True
            ),
        ],
    )


def test_contract_validate_inputs_valid() -> None:
    contract = _make_contract()
    errors = contract.validate_inputs(
        {"requirements": "# Requirements", "architecture": "none"}
    )
    assert errors == []


def test_contract_validate_inputs_missing_required() -> None:
    contract = _make_contract()
    errors = contract.validate_inputs({})
    assert any("requirements" in e for e in errors)


def test_contract_validate_inputs_optional_ok() -> None:
    contract = _make_contract()
    # architecture is optional — only requirements is required
    errors = contract.validate_inputs({"requirements": "stuff"})
    assert errors == []


def test_contract_validate_outputs_valid() -> None:
    contract = _make_contract()
    errors = contract.validate_outputs(["source_code"])
    assert errors == []


def test_contract_validate_outputs_missing_required() -> None:
    contract = _make_contract()
    errors = contract.validate_outputs([])
    assert any("source_code" in e for e in errors)


def test_contract_round_trip_dict() -> None:
    contract = _make_contract()
    data = contract.to_dict()
    restored = AgentContract.from_dict(data)
    assert restored.agent_name == contract.agent_name
    assert len(restored.inputs) == 2
    assert restored.inputs[0].name == "requirements"
    assert restored.inputs[1].required is False
    assert restored.outputs[0].name == "source_code"


def test_contract_registry() -> None:
    registry = ContractRegistry()
    contract = _make_contract()
    registry.register(contract)
    assert registry.get("code_generator_agent") is contract
    assert registry.get("unknown") is None
    assert len(registry.all_contracts()) == 1
