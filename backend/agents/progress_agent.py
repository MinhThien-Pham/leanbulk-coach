from .config import AgentConfig
from backend.agents.tool_registry import get_progress_tools

def get_progress_agent_config() -> AgentConfig:
    return AgentConfig(
        name="ProgressAgent",
        purpose="Interpret weight trend, waist trend, adherence, and logs.",
        instruction=(
            "Use weekly averages and waist trend to evaluate progress. "
            "Avoid overreacting to single weigh-ins. "
            "Rely on trend tools rather than raw guesses."
        ),
        tools=get_progress_tools(),
        metadata={"capabilities": ["progress_tracking"]}
    )
