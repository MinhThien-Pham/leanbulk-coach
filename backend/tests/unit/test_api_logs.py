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

def create_test_user(client):
    res = client.post("/profiles", json={"sex": "male", "age": 25, "height_cm": 180.0})
    return res.json()["id"]

def test_body_metrics(client):
    uid = create_test_user(client)
    res = client.post("/logs/body", json={"user_id": uid, "weight_kg": 75.0, "waist_cm": 80.0})
    assert res.status_code == 200
    
    res = client.get(f"/logs/body/{uid}/latest")
    assert res.status_code == 200
    assert res.json()["weight_kg"] == 75.0
    
    res = client.get(f"/logs/body/{uid}")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_workouts(client):
    uid = create_test_user(client)
    res = client.post("/logs/workouts", json={
        "user_id": uid, "exercise_name": "Bench Press", "reps": 8, "weight_kg": 60.0, "rir": 1.5
    })
    assert res.status_code == 200
    assert res.json()["rir"] == 1.5
    
    res = client.get(f"/logs/workouts/{uid}")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_nutrition_targets(client):
    uid = create_test_user(client)
    res = client.post("/logs/nutrition-targets", json={
        "user_id": uid, "target_kcal": 2500, "protein_g": 150
    })
    assert res.status_code == 200
    
    res = client.get(f"/logs/nutrition-targets/{uid}/latest")
    assert res.status_code == 200
    assert res.json()["target_kcal"] == 2500

def test_meals(client):
    uid = create_test_user(client)
    res = client.post("/logs/meals", json={
        "user_id": uid, "meal_name": "Chicken", "kcal": 500, "protein_g": 50
    })
    assert res.status_code == 200
    
    res = client.get(f"/logs/meals/{uid}")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_safety_flags(client):
    uid = create_test_user(client)
    res = client.post("/logs/safety-flags", json={
        "user_id": uid, "flag_type": "waist_creep", "severity": "high", "message": "Warning"
    })
    assert res.status_code == 200
    flag_id = res.json()["id"]
    
    res = client.get(f"/logs/safety-flags/{uid}/open")
    assert res.status_code == 200
    assert len(res.json()) == 1
    
    res = client.post(f"/logs/safety-flags/{flag_id}/resolve")
    assert res.status_code == 200
    
    res = client.get(f"/logs/safety-flags/{uid}/open")
    assert res.status_code == 200
    assert len(res.json()) == 0

def test_invalid_user(client):
    res = client.post("/logs/body", json={"user_id": 999, "weight_kg": 75.0})
    assert res.status_code == 404
