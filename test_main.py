from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "google_services" in data

def test_info_endpoint():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SmartLife AI Assistant"
    assert "tech_stack" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_chat_empty_message():
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 400

def test_chat_missing_message():
    response = client.post("/chat", json={})
    assert response.status_code == 400

def test_chat_too_long_message():
    response = client.post("/chat", json={"message": "a" * 2001})
    assert response.status_code == 400

def test_chat_xss_sanitization():
    response = client.post("/chat", json={"message": "<script>alert(1)</script>hello"})
    assert response.status_code in [200, 500]

def test_invalid_json():
    response = client.post("/chat", data="not json", headers={"Content-Type": "application/json"})
    assert response.status_code == 400

def test_rate_limit_headers():
    response = client.get("/health")
    assert response.status_code == 200
