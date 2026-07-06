import pytest
from backend.workflows.demo_flow import run_local_demo_flow

@pytest.mark.asyncio
async def test_run_local_demo_flow():
    result = await run_local_demo_flow()
    
    assert "profile" in result
    assert "contexts" in result
    assert "summary" in result
    assert "metadata" in result
    
    metadata = result["metadata"]
    assert metadata["live_llm_calls"] is False
    assert metadata["flow"] == "local_demo"
    assert metadata["activity_level"] == "moderately_active"
    
    summary = result["summary"]
    assert summary["user_name"] == "Demo User"
    assert summary["calorie_target_kcal"] > 0
    assert summary["protein_target_g"] > 0
    
    contexts = result["contexts"]
    assert len(contexts["body_history_context"]) >= 4
    assert len(contexts["recent_workout_context"]) >= 2
    assert len(contexts["recent_meal_context"]) >= 2
