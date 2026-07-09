"""Planning agent.

This agent accepts architecture design and produces a detailed project plan
including milestones, phases, tasks, and timeline estimates.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class PlanningAgent(Agent):
    name = "planning"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a project plan from architecture design.

        Expects inputs:
        - artifact: (optional) The architecture artifact from a prior step
        - architecture_text: (optional) Raw architecture text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The project plan document (milestones, phases, tasks, timeline)
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # Extract architecture from artifact or raw text
        architecture_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            architecture_text = inputs["artifact"].get("content", "")
        if not architecture_text:
            architecture_text = inputs.get("architecture_text", "")

        if not architecture_text:
            return {"status": "error", "message": "No architecture provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a project manager and planning expert. Based on the following architecture design,
produce a detailed project plan including:

1. Project Overview and Objectives
2. Milestones (key deliverables and dates)
3. Project Phases (discovery, design, development, testing, deployment)
   - For each phase: duration, key activities, deliverables, dependencies
4. Work Breakdown Structure (tasks and subtasks)
   - Estimate effort for each major task (in story points or days)
5. Resource Requirements (team roles and count)
6. Risk Assessment and Mitigation Plan
7. Success Criteria and KPIs
8. Timeline (Gantt chart description)

Architecture Design:
{architecture_text}

Provide the comprehensive project plan:"""

        result = provider.generate(prompt)
        plan_text = result.get("response", "")

        return {
            "artifact": {
                "type": "project_plan",
                "content": plan_text,
            },
            "artifact_name": "project_plan_v1",
            "status": "success",
        }
