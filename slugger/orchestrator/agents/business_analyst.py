"""Business Analyst agent.

This agent accepts requirements and produces a business analysis document
including user stories, acceptance criteria and business value assessment.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class BusinessAnalystAgent(Agent):
    name = "business_analyst"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Produce business analysis from requirements.

        Expects inputs:
        - artifact: (optional) The requirements artifact from a prior step
        - requirements_text: (optional) Raw requirements text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The business analysis document (user stories, acceptance criteria)
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # try to extract requirements from artifact or raw text
        requirements_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            requirements_text = inputs["artifact"].get("content", "")
        if not requirements_text:
            requirements_text = inputs.get("requirements_text", "")

        if not requirements_text:
            return {"status": "error", "message": "No requirements provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a business analyst. Analyze the following requirements and produce:
1. User Stories (in the format: As a <role>, I want <feature>, so that <benefit>)
2. Acceptance Criteria for each story
3. Business Value Assessment (high/medium/low)
4. Risks and Dependencies

Requirements:
{requirements_text}

Provide the business analysis:"""

        result = provider.generate(prompt)
        analysis_text = result.get("response", "")

        return {
            "artifact": {
                "type": "business_analysis",
                "content": analysis_text,
            },
            "artifact_name": "business_analysis_v1",
            "status": "success",
        }
