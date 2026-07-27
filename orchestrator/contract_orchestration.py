"""Orchestration over the organisation-owned AI-SDLC wire contracts.

This module deliberately does not declare JSON schemas or enums.  The mappings it
receives are the wire objects validated by the shared-contract validator supplied
by the embedding service; the small wrappers only provide typed access.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence
import warnings


class ContractError(ValueError):
    """Raised when an external contract or an orchestration gate fails."""


class CanonicalValidator(Protocol):
    """Adapter implemented by the canonical contracts package/schema registry."""

    def __call__(self, kind: str, payload: Mapping[str, Any]) -> None: ...


@dataclass(frozen=True)
class TaskContract:
    """Typed view of a validated canonical task; not a schema definition."""

    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(dict(self.payload))


@dataclass(frozen=True)
class ExecutionInput:
    """Typed view of a validated canonical execution input."""

    payload: Mapping[str, Any]

    @property
    def correlation_id(self) -> str:
        return str(self.payload["correlation_id"])

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(dict(self.payload))


@dataclass(frozen=True)
class ExecutionResult:
    """Typed view of a validated canonical execution result."""

    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(dict(self.payload))


@dataclass
class ChildExecution:
    """Internal bookkeeping for one canonical child execution."""

    key: str
    execution_input: dict[str, Any]
    result: dict[str, Any] | None = None


@dataclass
class OrchestrationState:
    """Resumable internal state.  Its fields never enter the result contract."""

    orchestration_id: str
    root_input: dict[str, Any]
    steps: list[str] | None = None
    children: list[ChildExecution] = field(default_factory=list)
    final_result: dict[str, Any] | None = None
    result_delivered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "orchestration_id": self.orchestration_id,
            "root_input": self.root_input,
            "steps": self.steps,
            "children": [
                {"key": child.key, "execution_input": child.execution_input, "result": child.result}
                for child in self.children
            ],
            "final_result": self.final_result,
            "result_delivered": self.result_delivered,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "OrchestrationState":
        return cls(
            orchestration_id=str(value["orchestration_id"]),
            root_input=dict(value["root_input"]),
            steps=list(value["steps"]) if value.get("steps") is not None else None,
            children=[ChildExecution(**dict(item)) for item in value.get("children", [])],
            final_result=dict(value["final_result"]) if value.get("final_result") else None,
            result_delivered=bool(value.get("result_delivered", False)),
        )


class JsonStateStore:
    """Atomic file persistence for resumable orchestration state."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    def load(self, orchestration_id: str) -> OrchestrationState | None:
        path = self.directory / f"{orchestration_id}.json"
        return OrchestrationState.from_dict(json.loads(path.read_text())) if path.exists() else None

    def save(self, state: OrchestrationState) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        destination = self.directory / f"{state.orchestration_id}.json"
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(json.dumps(state.to_dict(), sort_keys=True), encoding="utf-8")
        temporary.replace(destination)


def migrate_legacy_input(payload: Mapping[str, Any], *, contract_version: str) -> dict[str, Any]:
    """Translate the former Slugger MVP input once, before the production path.

    ``idea``, ``project_name`` and ``github_repository`` are deprecated.  The
    returned object must still pass the configured canonical validator.
    """

    if not ({"idea", "project_name"} & payload.keys()):
        return deepcopy(dict(payload))
    warnings.warn(
        "Slugger legacy fields idea/project_name/github_repository are deprecated; send a canonical execution input",
        DeprecationWarning,
        stacklevel=2,
    )
    repository = payload.get("target_repository", payload.get("github_repository"))
    source_url = payload.get("source_issue_url", "")
    return {
        "contract_version": contract_version,
        "execution_id": str(payload.get("request_identity", payload.get("run_id", "legacy"))),
        "correlation_id": str(payload.get("correlation_id", payload.get("request_identity", "legacy"))),
        "source_issue": {"url": source_url, "number": payload.get("source_issue_number")},
        "approval_status": payload.get("approval_status", "approved"),
        "executor": payload.get("executor", "codex"),
        "priority": payload.get("priority", "normal"),
        "task_type": payload.get("task_type", "implementation"),
        "target_repository": repository,
        "dependencies": list(payload.get("dependencies", [])),
        "draft_only": payload.get("draft_only", True),
        "instructions": payload.get("idea", ""),
        "metadata": {"project_name": payload.get("project_name", "")},
    }


class ContractOrchestrator:
    """A single orchestration path around canonical inputs and results."""

    def __init__(self, *, contract_version: str, validator: CanonicalValidator,
                 registered_repositories: set[str], state_store: JsonStateStore,
                 execute: Callable[[Mapping[str, Any]], Mapping[str, Any]],
                 is_success: Callable[[Mapping[str, Any]], bool],
                 post_result: Callable[[Mapping[str, Any], Mapping[str, Any]], None]) -> None:
        self.contract_version = contract_version
        self.validator = validator
        self.registered_repositories = registered_repositories
        self.state_store = state_store
        self.execute = execute
        self.is_success = is_success
        self.post_result = post_result

    def ingest(self, payload: Mapping[str, Any], *, kind: str = "execution_input") -> ExecutionInput:
        value = migrate_legacy_input(payload, contract_version=self.contract_version)
        if value.get("contract_version") != self.contract_version:
            raise ContractError("unsupported contract_version")
        if kind == "task":
            self.validator("task", value)
            value = self._task_to_execution_input(value)
        self.validator("execution_input", value)
        self._enforce_gates(value)
        return ExecutionInput(value)

    def _task_to_execution_input(self, task: Mapping[str, Any]) -> dict[str, Any]:
        value = deepcopy(dict(task))
        value["execution_id"] = value.get("execution_id", value.get("task_id"))
        return value

    def _enforce_gates(self, value: Mapping[str, Any]) -> None:
        if value.get("target_repository") not in self.registered_repositories:
            raise ContractError("target repository is not registered")
        if value.get("dependencies"):
            raise ContractError("dependencies are unresolved")
        if str(value.get("executor", "")).lower() != "codex":
            raise ContractError("executor is not Codex")
        if value.get("draft_only") is not True:
            raise ContractError("draft_only must be true")

    def _child(self, root: ExecutionInput, instruction: str, index: int) -> ChildExecution:
        key = hashlib.sha256(f"{root.payload['execution_id']}:{index}:{instruction}".encode()).hexdigest()[:24]
        value = root.to_dict()
        value["execution_id"] = key
        value["parent_execution_id"] = root.payload["execution_id"]
        value["instructions"] = instruction
        self.validator("execution_input", value)
        return ChildExecution(key, value)

    def run(self, payload: Mapping[str, Any], *, steps: Sequence[str] | None = None,
            kind: str = "execution_input") -> ExecutionResult:
        root = self.ingest(payload, kind=kind)
        orchestration_id = str(root.payload["execution_id"])
        state = self.state_store.load(orchestration_id) or OrchestrationState(orchestration_id, root.to_dict())
        requested = list(steps or [str(root.payload["instructions"])])
        if state.steps is None:
            state.steps = requested
            self.state_store.save(state)
        elif requested != state.steps:
            raise ContractError("steps do not match the persisted orchestration plan")
        if state.final_result is not None:
            self.validator("execution_result", state.final_result)
            self._deliver_result(root, state)
            return ExecutionResult(state.final_result)
        by_key = {child.key: child for child in state.children}
        for index, instruction in enumerate(state.steps):
            candidate = self._child(root, instruction, index)
            child = by_key.get(candidate.key)
            if child is None:
                child = candidate
                state.children.append(child)
                by_key[child.key] = child
                self.state_store.save(state)
            if child.result is None:
                result = dict(self.execute(child.execution_input))
                self.validator("execution_result", result)
                if result.get("correlation_id") != root.correlation_id:
                    raise ContractError("child result changed correlation_id")
                child.result = result
                self.state_store.save(state)
            if not self.is_success(child.result):
                break
        if any(child.result is None for child in state.children):
            raise ContractError("cannot finalize while a persisted child is unresolved")
        state.final_result = self._aggregate(root, state.children)
        self.validator("execution_result", state.final_result)
        self.state_store.save(state)
        self._deliver_result(root, state)
        return ExecutionResult(state.final_result)

    def _deliver_result(self, root: ExecutionInput, state: OrchestrationState) -> None:
        """Post a persisted result until delivery has been acknowledged locally."""

        if state.result_delivered:
            return
        assert state.final_result is not None
        self.post_result(root.payload["source_issue"], state.final_result)
        state.result_delivered = True
        self.state_store.save(state)

    def _aggregate(self, root: ExecutionInput, children: Sequence[ChildExecution]) -> dict[str, Any]:
        results = [child.result for child in children if child.result is not None]
        failed = next((result for result in results if not self.is_success(result)), None)
        result = deepcopy(failed or results[-1]) if results else {}
        result.update({
            "contract_version": self.contract_version,
            "execution_id": root.payload["execution_id"],
            "correlation_id": root.correlation_id,
            "source_issue": deepcopy(root.payload["source_issue"]),
            "status": (failed or results[-1])["status"],
            "summary": f"Orchestration completed {len(results)} of {len(children)} child executions."
            if not failed else f"Orchestration stopped after child failure ({len(results)} attempted).",
        })
        return result
