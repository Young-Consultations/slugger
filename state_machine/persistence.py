"""State machine persistence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from state_machine.models import StateMachineInstance


class StatePersistence:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def save(self, instance: StateMachineInstance) -> None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload[instance.instance_id] = asdict(instance)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self, instance_id: str) -> StateMachineInstance | None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        raw = payload.get(instance_id)
        if raw is None:
            return None
        return StateMachineInstance(**raw)
