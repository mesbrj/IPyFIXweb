
from pytest import fixture
from fastapi.testclient import TestClient

from src.adapters.web_api.fastapi.web_server import web_app


@fixture
def client():
    return TestClient(web_app)

@fixture
def time_series_uuid():
    return [
        "264c3408-aec2-59fb-9712-f2f5a555d982",
        "1164a4ac-1415-4316-a455-1f8d650348b2",
        "00000000-0000-0000-0000-000000000000"
    ]


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

def test_fake_time_series(client, time_series_uuid):
    response = client.get(f"/api/v1/test/time_series/{time_series_uuid[0]}")
    data = response.json()

    assert response.status_code == 200
    assert data["ts_uuid"] == time_series_uuid[0]
    assert data["measurements_list"] == []

    response = client.get(f"/api/v1/test/time_series/{time_series_uuid[1]}")
    data = response.json()

    assert response.status_code == 200
    assert data["measurements"][0]["tags"] == ["HTTPS"]
    assert data["measurements"][1]["data_sources_info"][2] == ["AVERAGE", 7200, 7084, 1, 0.5]

    response = client.get(f"/api/v1/test/time_series/{time_series_uuid[2]}")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"]["error"] == "Time series instance not found"
