from fastapi.testclient import TestClient
from backend.app.main import create_app

def test_get_demo_local():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.get("/demo/local")
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "contexts" in data
    assert "summary" in data
    assert "metadata" in data
    
    assert data["metadata"]["live_llm_calls"] is False
    assert data["metadata"]["activity_level"] == "moderately_active"
