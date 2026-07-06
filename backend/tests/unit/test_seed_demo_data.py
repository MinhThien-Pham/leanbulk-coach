import pytest
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db
from backend.workflows.seed_demo_data import seed_demo_profile

@pytest.mark.asyncio
async def test_seed_demo_profile():
    # Set up in-memory sqlite
    engine = create_sqlite_async_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    factory = create_async_session_factory(engine)
    
    async with factory() as session:
        res = await seed_demo_profile(session)
        
        assert res["demo_only"] is True
        assert res["profile"] is not None
        assert res["profile"]["display_name"] == "Demo LeanBulk User"
        assert res["profile"]["id"] is not None
        
        assert res["created"]["body_logs"] >= 6
        assert res["created"]["workout_logs"] >= 4
        assert res["created"]["meal_logs"] >= 3
        assert res["created"]["safety_flags"] >= 1
        
        # Check context
        ctx = res["context"]
        assert len(ctx["body_history_context"]) >= 6
        assert len(ctx["open_safety_context"]) >= 1
        assert ctx["open_safety_context"][0]["flag_type"] == "pain_flag"
        
        # Check summary
        summary = res["summary"]
        assert len(summary["next_actions"]) >= 1
        assert summary["goal"] == "lean_bulk"
        assert summary["user_name"] == "Demo LeanBulk User"
        
    await engine.dispose()
