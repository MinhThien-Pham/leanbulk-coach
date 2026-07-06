from .config import AgentConfig
from backend.agents.tool_registry import get_training_tools

def get_training_agent_config() -> AgentConfig:
    return AgentConfig(
        name="TrainingAgent",
        purpose="Give workout/progression recommendations.",
        instruction=(
            "Provide hypertrophy-focused workout recommendations. "
            "Prefer double progression concept when explaining progression. "
            "Warn the user that sharp pain means they should stop immediately and seek professional medical help."
        ),
        tools=get_training_tools(),
        metadata={"capabilities": ["workout_planning"]}
    )
