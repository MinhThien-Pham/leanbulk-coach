"""
ADK-compatible entrypoint for LeanBulk Coach agents.
"""
from backend.agents.adk_adapter import create_root_adk_agent, is_google_adk_available
from backend.agents.root_agent import get_root_agent_config

if is_google_adk_available():
    # Real ADK agent
    try:
        root_agent = create_root_adk_agent()
    except Exception:
        # Fallback for offline/unit-test mode if config fails
        root_agent = get_root_agent_config()
else:
    # Fallback for offline/unit-test mode
    root_agent = get_root_agent_config()
