"""State machine models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class State:
    name: str
    is_terminal: bool = False


@dataclass(slots=True)
class Transition:
    trigger: str
    source: str
    target: str


@dataclass(slots=True)
class StateMachineDefinition:
    name: str
    states: list[State]
    transitions: list[Transition]
    initial_state: str


@dataclass(slots=True)
class StateMachineInstance:
    instance_id: str
    definition_name: str
    current_state: str
    history: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
