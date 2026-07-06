from .config import AgentConfig
from backend.agents.tool_registry import get_safety_tools

def get_safety_agent_config() -> AgentConfig:
    return AgentConfig(
        name="SafetyAgent",
        purpose="Check unsafe calorie targets, rapid weight changes, waist creep, risky advice.",
        instruction=(
            "You have the authority to override other agents if safety is compromised. "
            "No medical diagnosis, no extreme dieting, no steroid advice. "
            "Always prioritize user safety and flag unsafe trends immediately."
        ),
        tools=get_safety_tools(),
        metadata={"capabilities": ["safety_override"], "is_safety_agent": True}
    )
