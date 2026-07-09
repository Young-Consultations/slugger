"""Architecture agent.

This agent accepts requirements and business analysis, and produces a
detailed architecture design including components, interactions, and
technology choices.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class ArchitectureAgent(Agent):
    name = "architecture"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Produce architecture design from requirements and analysis.

        Expects inputs:
        - artifact: (optional) The business analysis artifact from a prior step
        - requirements_text: (optional) Raw requirements text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The architecture design document
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # Extract requirements or analysis from artifact or raw text
        context_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            context_text = inputs["artifact"].get("content", "")
        if not context_text:
            context_text = inputs.get("requirements_text", "")

        if not context_text:
            return {"status": "error", "message": "No context provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a software architect. Based on the following requirements and business analysis,
produce a detailed architecture design including:

1. System Overview (high-level diagram description)
2. Component Architecture (key components and responsibilities)
3. Technology Stack Recommendations (languages, frameworks, databases)
4. Integration Points and Data Flow
5. Scalability and Performance Considerations
6. Security Architecture
7. Deployment Strategy

Context:
{context_text}

Provide the architecture design:"""

        result = provider.generate(prompt)
        architecture_text = result.get("response", "")

        return {
            "artifact": {
                "type": "architecture",
                "content": architecture_text,
            },
            "artifact_name": "architecture_v1",
            "status": "success",
        }
