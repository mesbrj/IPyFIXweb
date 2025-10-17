
from pytest import fixture
from fastapi.testclient import TestClient

from src.adapters.web_api.fastapi.web_server import web_app

@fixture
def client():
    return TestClient(web_app)

def test_health_check(client):
    response = client.get("/api/v1/test/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_export_fake_task(client):
    response = client.post("/api/v1/test/file_exporter/export_task")
    data = response.json()
    assert response.status_code == 200
    assert "task_id" in data
    assert data["status"] == "export task started"