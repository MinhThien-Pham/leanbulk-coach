from .config import AgentConfig
from backend.agents.tool_registry import get_nutrition_tools

def get_nutrition_agent_config() -> AgentConfig:
    return AgentConfig(
        name="NutritionAgent",
        purpose="Calculate calorie target, protein target, and suggest meals.",
        instruction=(
            "Prioritize lean bulk muscle gain while limiting fat gain. "
            "You must avoid making any medical claims. "
            "You must use deterministic tools for all math, do not estimate calories or protein without tools."
        ),
        tools=get_nutrition_tools(),
        metadata={"capabilities": ["nutrition_planning"]}
    )
