import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.app.main import create_app
from backend.app.dependencies import get_session
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db

@pytest.fixture(name="client")
def client_fixture():
    engine = create_sqlite_async_engine("sqlite+aiosqlite:///:memory:")
    
    loop = asyncio.new_event_loop()
    loop.run_until_complete(init_db(engine))
    
    session_maker = create_async_session_factory(engine)
    app = create_app(init_db_on_startup=False)
    
    async def override_get_session():
        async with session_maker() as session:
            yield session
            
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as c:
        yield c

    loop.run_until_complete(engine.dispose())
    loop.close()

def test_api_seed_demo_profile(client):
    # 1. Post to seed demo profile
    res = client.post("/seed/demo-profile")
    assert res.status_code == 200
    data = res.json()
    
    assert data["demo_only"] is True
    profile = data["profile"]
    assert profile["id"] is not None
    assert profile["display_name"] == "Demo LeanBulk User"
    
    assert data["created"]["body_logs"] >= 6
    assert data["created"]["workout_logs"] >= 4
    assert data["created"]["meal_logs"] >= 3
    assert data["created"]["safety_flags"] >= 1
    
    # 2. Get user context of the seeded profile
    res_ctx = client.get(f"/context/{profile['id']}")
    assert res_ctx.status_code == 200
    ctx_data = res_ctx.json()
    assert len(ctx_data["body_history_context"]) >= 6
    assert len(ctx_data["open_safety_context"]) >= 1
