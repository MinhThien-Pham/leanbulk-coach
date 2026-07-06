from fastapi.testclient import TestClient
from backend.app.main import create_app

def test_list_evals():
    app = create_app(init_db_on_startup=False)
    with TestClient(app) as client:
        response = client.get("/evals")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert data["total"] >= 12
        assert "cases" in data
        assert len(data["cases"]) == data["total"]
        case = data["cases"][0]
        assert "id" in case
        assert "category" in case
        assert "description" in case

def test_run_evals():
    app = create_app(init_db_on_startup=False)
    with TestClient(app) as client:
        response = client.post("/evals/run")
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] == 0
        assert data["score"] == 1.0

def test_get_eval_report():
    app = create_app(init_db_on_startup=False)
    with TestClient(app) as client:
        response = client.get("/evals/report")
        assert response.status_code == 200
        data = response.json()
        assert "Evaluation Report" in data["report"]
        assert data["summary"]["total"] >= 12
        if "live_llm_calls" in data:
            assert data["live_llm_calls"] is False
