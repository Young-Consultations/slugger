from pathlib import Path

from state_machine import (
    State,
    StateMachineDefinition,
    StateMachineEngine,
    StatePersistence,
    Transition,
)


def test_state_machine_transition_persists() -> None:
    path = Path("tests/state-machine-store.json")
    if path.exists():
        path.unlink()
    engine = StateMachineEngine(StatePersistence(path))
    engine.register(
        StateMachineDefinition(
            name="delivery",
            states=[State("draft"), State("done", is_terminal=True)],
            transitions=[Transition(trigger="finish", source="draft", target="done")],
            initial_state="draft",
        )
    )
    instance = engine.create_instance("delivery")
    updated = engine.process(instance.instance_id, "finish")
    assert updated.current_state == "done"
    path.unlink(missing_ok=True)
