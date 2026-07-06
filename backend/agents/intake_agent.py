from .config import AgentConfig

def get_intake_agent_config() -> AgentConfig:
    return AgentConfig(
        name="IntakeAgent",
        purpose="Collect and normalize user profile inputs.",
        instruction=(
            "Collect and normalize user profile inputs. "
            "Validate sex, age, height, bodyweight, goal, target weight. "
            "Do not guess missing information; ask clarifying questions if needed."
        ),
        tools=[],  # DB repositories will be referenced here
        metadata={"capabilities": ["profile_management"]}
    )
