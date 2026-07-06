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

def test_get_context(client):
    res = client.post("/profiles", json={"sex": "male", "age": 25, "height_cm": 180.0})
    uid = res.json()["id"]
    
    client.post("/logs/body", json={"user_id": uid, "weight_kg": 75.0, "waist_cm": 80.0})
    client.post("/logs/workouts", json={"user_id": uid, "exercise_name": "Bench", "reps": 8})
    client.post("/logs/nutrition-targets", json={"user_id": uid, "target_kcal": 2500, "protein_g": 150})
    client.post("/logs/meals", json={"user_id": uid, "meal_name": "Chicken", "kcal": 500, "protein_g": 50})
    
    res = client.get(f"/context/{uid}")
    assert res.status_code == 200
    data = res.json()
    assert "profile_context" in data
    assert "latest_body_context" in data
    assert "body_history_context" in data
    assert "latest_nutrition_context" in data
    assert "recent_workout_context" in data
    assert "recent_meal_context" in data
    assert "open_safety_context" in data
    assert "progress_summary_context" in data
    
    assert data["latest_body_context"]["weight_kg"] == 75.0

def test_get_context_not_found(client):
    res = client.get("/context/999")
    assert res.status_code == 404
