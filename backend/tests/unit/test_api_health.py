from fastapi.testclient import TestClient
from backend.app.main import create_app

def test_get_health():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["live_llm_calls"] is False
