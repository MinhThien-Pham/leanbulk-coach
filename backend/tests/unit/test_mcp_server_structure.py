import pytest
from backend.mcp_server.server import MCP_TOOLS_REGISTRY, MCP_PUBLIC_TOOL_REGISTRY, get_mcp_server

def test_mcp_server_registry_exists_and_read_only():
    assert len(MCP_TOOLS_REGISTRY) == 8
    
    names = [func.__name__ for func in MCP_TOOLS_REGISTRY]
    assert "get_profile_context" in names
    
    # Assert no write operations exist in names
    for name in names:
        assert not name.startswith("add_")
        assert not name.startswith("create_")
        assert not name.startswith("update_")
        assert not name.startswith("delete_")
        assert not name.startswith("resolve_")

def test_get_mcp_server_safe_import():
    server = get_mcp_server()
    # If mcp is installed, it returns FastMCP instance, else None.
    # We just ensure it doesn't crash on import/invocation.
    assert server is None or type(server).__name__ == "FastMCP"

@pytest.mark.asyncio
async def test_mcp_wrappers_call_with_session(monkeypatch):
    # Mock _with_session to just return a known dict
    async def fake_with_session(func, *args, **kwargs):
        return {"called_func": func.__name__, "args": args, "kwargs": kwargs}
    
    monkeypatch.setattr("backend.mcp_server.server._with_session", fake_with_session)
    
    assert "read_profile_context" in MCP_PUBLIC_TOOL_REGISTRY
    assert "read_body_history_context" in MCP_PUBLIC_TOOL_REGISTRY
    
    wrapper = MCP_PUBLIC_TOOL_REGISTRY["read_profile_context"]
    res = await wrapper(user_id=123)
    assert res["called_func"] == "get_profile_context"
    assert res["kwargs"]["user_id"] == 123
    
    wrapper_list = MCP_PUBLIC_TOOL_REGISTRY["read_body_history_context"]
    res_list = await wrapper_list(user_id=123, limit=10)
    assert res_list["called_func"] == "get_body_history_context"
    assert res_list["kwargs"]["user_id"] == 123
    assert res_list["kwargs"]["limit"] == 10
