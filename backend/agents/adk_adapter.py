import logging
from typing import Any, Optional
from backend.agents.config import AgentConfig
from backend.agents.root_agent import get_root_agent_config, get_sub_agents

logger = logging.getLogger(__name__)

def is_google_adk_available() -> bool:
    try:
        get_adk_agent_class()
        return True
    except ImportError:
        return False

def get_adk_agent_class() -> Any:
    try:
        from google.adk.agents.llm_agent import Agent
        return Agent
    except ImportError:
        try:
            from google.adk.agents import Agent
            return Agent
        except ImportError:
            raise ImportError("Google ADK Agent class could not be imported.")

def create_adk_agent_from_config(config: AgentConfig, *, model: str = "gemini-flash-latest") -> Any:
    Agent = get_adk_agent_class()
    
    # Try to construct the agent mapping fields. We only map what's commonly supported.
    kwargs = {
        "model": model,
        "name": config.name,
        "instruction": config.instruction,
        "tools": config.tools,
    }
    
    try:
        agent = Agent(**kwargs)
        return agent
    except TypeError:
        # Fallback if basic kwargs fail
        raise ValueError("Failed to instantiate ADK Agent with standard config.")

def create_root_adk_agent(*, model: str = "gemini-flash-latest") -> Any:
    root_config = get_root_agent_config()
    
    # In a real implementation we might pass sub-agents to the root.
    # For now, we embed the sub-agent names in the root config's metadata 
    # (already done in get_root_agent_config) and just create the root agent.
    root_adk_agent = create_adk_agent_from_config(root_config, model=model)
    return root_adk_agent
