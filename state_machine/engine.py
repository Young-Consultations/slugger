"""State machine engine."""

from __future__ import annotations

from uuid import uuid4

from state_machine.models import StateMachineDefinition, StateMachineInstance
from state_machine.persistence import StatePersistence


class StateMachineEngine:
    def __init__(self, persistence: StatePersistence) -> None:
        self.persistence = persistence
        self._definitions: dict[str, StateMachineDefinition] = {}

    def register(self, definition: StateMachineDefinition) -> None:
        self._definitions[definition.name] = definition

    def create_instance(self, definition_name: str) -> StateMachineInstance:
        definition = self._definitions[definition_name]
        instance = StateMachineInstance(instance_id=str(uuid4()), definition_name=definition.name, current_state=definition.initial_state, history=[definition.initial_state])
        self.persistence.save(instance)
        return instance

    def process(self, instance_id: str, trigger: str) -> StateMachineInstance:
        instance = self.persistence.load(instance_id)
        if instance is None:
            raise KeyError(f'Unknown state machine instance: {instance_id}')
        definition = self._definitions[instance.definition_name]
        for transition in definition.transitions:
            if transition.trigger == trigger and transition.source == instance.current_state:
                instance.current_state = transition.target
                instance.history.append(transition.target)
                self.persistence.save(instance)
                return instance
        raise ValueError(f'No transition for trigger {trigger!r} from state {instance.current_state!r}')
