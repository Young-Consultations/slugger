"""Project memory components.

Memory is intentionally small at this stage but structured to hold common
concerns: project metadata, conversation turns, decision history, prompt
history and an artifact registry.
"""
from typing import Any, Dict, List, Optional


class Memory:
    def __init__(self) -> None:
        self.project: Dict[str, Any] = {}
        self.conversations: List[Dict[str, Any]] = []
        self.decision_history: List[Dict[str, Any]] = []
        self.prompt_history: List[Dict[str, Any]] = []
        self.artifact_registry: Dict[str, Any] = {}

    def set_project_meta(self, key: str, value: Any) -> None:
        self.project[key] = value

    def get_project_meta(self, key: str, default: Optional[Any] = None) -> Any:
        return self.project.get(key, default)

    def add_conversation(self, role: str, content: str) -> None:
        self.conversations.append({"role": role, "content": content})

    def add_decision(self, summary: str, details: Dict[str, Any]) -> None:
        self.decision_history.append({"summary": summary, "details": details})

    def add_prompt(self, prompt: str, provider: str) -> None:
        self.prompt_history.append({"prompt": prompt, "provider": provider})

    def register_artifact(self, name: str, metadata: Dict[str, Any]) -> None:
        self.artifact_registry[name] = metadata

