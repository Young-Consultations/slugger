"""Initial tests for the orchestrator scaffold.

These tests verify the minimal contracts for providers, memory and the
workflow engine. They are intentionally small and focused to support TDD.
"""
from slugger.orchestrator.ai_providers.openai_provider import OpenAIProvider
from slugger.orchestrator.memory import Memory
from slugger.orchestrator.workflow import WorkflowEngine
from slugger.orchestrator.agents.base import Agent
from slugger.orchestrator.agent_manager import AgentManager
from typing import Dict


class EchoAgent(Agent):
    name = "echo"

    def execute(self, inputs: Dict[str, str]) -> Dict[str, str]:
        message = inputs.get("message", "")
        return {"echo": message}


def test_openai_provider_stub():
    p = OpenAIProvider(api_key=None)
    out = p.generate("hello")
    assert out["provider"] == "openai"
    assert "stubbed" in out["response"]


def test_memory_basics():
    m = Memory()
    m.set_project_meta("name", "slugger")
    assert m.get_project_meta("name") == "slugger"
    m.add_prompt("hello", provider="openai")
    assert len(m.prompt_history) == 1


def test_agent_manager_and_workflow():
    manager = AgentManager()
    agent = EchoAgent()
    manager.register(agent)
    assert manager.get("echo") is agent

    engine = WorkflowEngine()

    def step_one(ctx: Dict[str, str]) -> Dict[str, str]:
        return {"message": "hi"}

    def step_two(ctx: Dict[str, str]) -> Dict[str, str]:
        # simulate calling the echo agent
        a = manager.get("echo")
        assert a is not None
        return a.execute({"message": ctx["message"]})

    result = engine.run_sequential([step_one, step_two])
    assert result.get("echo") == "hi"
