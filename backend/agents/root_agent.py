from .config import AgentConfig
from .intake_agent import get_intake_agent_config
from .nutrition_agent import get_nutrition_agent_config
from .training_agent import get_training_agent_config
from .progress_agent import get_progress_agent_config
from .safety_agent import get_safety_agent_config

def get_sub_agents() -> list[AgentConfig]:
    return [
        get_intake_agent_config(),
        get_nutrition_agent_config(),
        get_training_agent_config(),
        get_progress_agent_config(),
        get_safety_agent_config()
    ]

def get_root_agent_config() -> AgentConfig:
    return AgentConfig(
        name="LeanBulkCoachAgent",
        purpose="Orchestrate sub-agents and interact with the user safely.",
        instruction=(
            "You are the LeanBulk Coach root agent. Orchestrate the sub-agents to assist the user. "
            "Ask clarifying questions only when required. "
            "Use tools for calculations. "
            "Prefer safe, beginner-friendly, hypertrophy-focused guidance. "
            "SafetyAgent can override other recommendations."
        ),
        tools=[],  # Root delegates
        metadata={"sub_agents": [a.name for a in get_sub_agents()]}
    )
