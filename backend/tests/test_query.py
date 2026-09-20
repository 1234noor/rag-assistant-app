from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test that the health endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_happy_path():
    """Test that a valid question returns a grounded answer with sources."""
    response = client.post("/query", json={"question": "What is stemming in NLP?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_query_invalid_input():
    """Test that an invalid request (missing 'question' field) returns 422."""
    response = client.post("/query", json={"wrong_field": "some value"})
    assert response.status_code == 422