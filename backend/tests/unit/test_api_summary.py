from fastapi.testclient import TestClient
from backend.app.main import create_app

def test_summary_normal():
    app = create_app()
    client = TestClient(app)
    response = client.post("/summary/build", json={
        "profile_context": {"display_name": "Test User"},
        "latest_body_context": {"weight_kg": 75.0, "waist_cm": 80.0}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "Test User"
    assert data["current_weight_kg"] == 75.0

def test_summary_empty():
    app = create_app()
    client = TestClient(app)
    response = client.post("/summary/build", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] is None
    assert "Complete intake profile" in data["next_actions"][0]
