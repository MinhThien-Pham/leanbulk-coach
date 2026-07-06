from fastapi.testclient import TestClient
from backend.app.main import create_app

def test_calorie_target_valid():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.post("/tools/calorie-target", json={
        "weight_kg": 75.0,
        "height_cm": 180.0,
        "age": 25,
        "sex": "male"
    })
    assert response.status_code == 200
    assert response.json()["target_kcal"] > 0

def test_calorie_target_invalid():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.post("/tools/calorie-target", json={
        "weight_kg": -10.0,
        "height_cm": 180.0,
        "age": 25,
        "sex": "male"
    })
    assert response.status_code == 400

def test_protein_target_valid():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.post("/tools/protein-target", json={
        "weight_kg": 75.0
    })
    assert response.status_code == 200
    assert response.json()["protein_g"] > 0

def test_protein_target_invalid():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.post("/tools/protein-target", json={
        "weight_kg": -10.0
    })
    assert response.status_code == 400

def test_meal_suggestions_valid():
    app = create_app(init_db_on_startup=False)
    client = TestClient(app)
    response = client.post("/tools/meal-suggestions", json={
        "target_kcal": 600,
        "target_protein_g": 40
    })
    assert response.status_code == 200
    assert "suggestions" in response.json()
