import pytest
from backend.agents.config import AgentConfig
from backend.agents.adk_adapter import (
    is_google_adk_available,
    get_adk_agent_class,
    create_adk_agent_from_config,
    create_root_adk_agent
)
from backend.agents import agent

class FakeAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

def test_is_google_adk_available_returns_bool():
    assert isinstance(is_google_adk_available(), bool)

def test_create_adk_agent_from_config(monkeypatch):
    monkeypatch.setattr("backend.agents.adk_adapter.get_adk_agent_class", lambda: FakeAgent)
    
    config = AgentConfig(
        name="TestAgent",
        purpose="Testing",
        instruction="Do something",
        tools=["fake_tool"]
    )
    
    ag = create_adk_agent_from_config(config, model="test-model")
    assert ag.kwargs["name"] == "TestAgent"
    assert ag.kwargs["instruction"] == "Do something"
    assert ag.kwargs["tools"] == ["fake_tool"]
    assert ag.kwargs["model"] == "test-model"

def test_create_root_adk_agent(monkeypatch):
    monkeypatch.setattr("backend.agents.adk_adapter.get_adk_agent_class", lambda: FakeAgent)
    
    root_agent = create_root_adk_agent(model="test-model")
    assert root_agent.kwargs["name"] == "LeanBulkCoachAgent"
    assert root_agent.kwargs["model"] == "test-model"

def test_entrypoint_imports_safely():
    # We already imported agent at the top
    assert agent.root_agent is not None
    # Depending on the environment, it's either an AgentConfig or a FakeAgent/RealAgent.
    # We just ensure it exposes 'name' directly or via kwargs.
    if hasattr(agent.root_agent, "name"):
        assert agent.root_agent.name == "LeanBulkCoachAgent"
    else:
        assert agent.root_agent.kwargs["name"] == "LeanBulkCoachAgent"
