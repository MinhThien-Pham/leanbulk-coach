import os
from backend.db.session import create_sqlite_async_engine, create_async_session_factory
from .context_tools import (
    get_profile_context,
    get_latest_body_context,
    get_body_history_context,
    get_latest_nutrition_context,
    get_recent_workout_context,
    get_recent_meal_context,
    get_open_safety_context,
    get_progress_summary_context
)

# Ensure no write operations are exposed. Only read-only context fetchers.
MCP_TOOLS_REGISTRY = [
    get_profile_context,
    get_latest_body_context,
    get_body_history_context,
    get_latest_nutrition_context,
    get_recent_workout_context,
    get_recent_meal_context,
    get_open_safety_context,
    get_progress_summary_context
]

def get_mcp_database_url() -> str:
    return os.environ.get("LEANBULK_DATABASE_URL", "sqlite+aiosqlite:///./leanbulk.db")

def create_mcp_session_factory(database_url: str | None = None):
    url = database_url or get_mcp_database_url()
    engine = create_sqlite_async_engine(url)
    return create_async_session_factory(engine), engine

async def _with_session(coro_func, *args, **kwargs):
    factory, engine = create_mcp_session_factory()
    try:
        async with factory() as session:
            return await coro_func(session, *args, **kwargs)
    finally:
        await engine.dispose()

async def read_profile_context(user_id: int) -> dict:
    """Read user profile context"""
    return await _with_session(get_profile_context, user_id=user_id)

async def read_latest_body_context(user_id: int) -> dict:
    """Read latest body metric"""
    return await _with_session(get_latest_body_context, user_id=user_id)

async def read_body_history_context(user_id: int, limit: int = 30) -> list:
    """Read body metric history"""
    return await _with_session(get_body_history_context, user_id=user_id, limit=limit)

async def read_latest_nutrition_context(user_id: int) -> dict:
    """Read latest nutrition target"""
    return await _with_session(get_latest_nutrition_context, user_id=user_id)

async def read_recent_workout_context(user_id: int, limit: int = 50) -> list:
    """Read recent workout logs"""
    return await _with_session(get_recent_workout_context, user_id=user_id, limit=limit)

async def read_recent_meal_context(user_id: int, limit: int = 50) -> list:
    """Read recent meal logs"""
    return await _with_session(get_recent_meal_context, user_id=user_id, limit=limit)

async def read_open_safety_context(user_id: int) -> list:
    """Read open safety flags"""
    return await _with_session(get_open_safety_context, user_id=user_id)

async def read_progress_summary_context(user_id: int, limit: int = 14) -> dict:
    """Read progress summary"""
    return await _with_session(get_progress_summary_context, user_id=user_id, limit=limit)

MCP_PUBLIC_TOOL_REGISTRY = {
    "read_profile_context": read_profile_context,
    "read_latest_body_context": read_latest_body_context,
    "read_body_history_context": read_body_history_context,
    "read_latest_nutrition_context": read_latest_nutrition_context,
    "read_recent_workout_context": read_recent_workout_context,
    "read_recent_meal_context": read_recent_meal_context,
    "read_open_safety_context": read_open_safety_context,
    "read_progress_summary_context": read_progress_summary_context,
}

def get_mcp_server():
    """
    Returns an MCP server instance exposing read-only tools, if the mcp package is installed.
    """
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("LeanBulkCoach")
        for tool_name, tool_func in MCP_PUBLIC_TOOL_REGISTRY.items():
            mcp.tool(name=tool_name)(tool_func)
        return mcp
    except ImportError:
        return None
