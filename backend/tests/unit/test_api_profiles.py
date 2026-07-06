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

def test_create_and_get_profile(client):
    res = client.post("/profiles", json={
        "sex": "male",
        "age": 25,
        "height_cm": 180.0,
        "display_name": "Test User"
    })
    assert res.status_code == 200
    p = res.json()
    assert p["id"] == 1
    assert p["display_name"] == "Test User"
    
    res = client.get("/profiles/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1
    
    res = client.get("/profiles")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_profile_not_found(client):
    res = client.get("/profiles/999")
    assert res.status_code == 404

def test_invalid_profile(client):
    res = client.post("/profiles", json={
        "sex": "male",
        "age": -5,
        "height_cm": 180.0
    })
    assert res.status_code == 400
