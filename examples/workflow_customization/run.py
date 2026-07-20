"""Workflow customization example — parse a local YAML workflow."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from validators import WorkflowValidator
from workflow import WorkflowParser


def main() -> None:
    workflow_path = Path(__file__).with_name("custom-workflow.yaml")
    definition = WorkflowParser(WorkflowValidator()).parse_file(workflow_path)

    print(f"Workflow: {definition.name} ({definition.version})")
    print(definition.description)
    for index, step in enumerate(definition.steps, start=1):
        outputs = ", ".join(step.outputs) or "none"
        print(f"{index}. {step.name} -> {step.agent} [outputs: {outputs}]")


if __name__ == "__main__":
    main()
