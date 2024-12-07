import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_rate_limiting(client):
    # Create API key first
    api_key = "test_key_123"
    headers = {"X-API-Key": api_key}

    # Make requests up to limit
    responses = []
    for _ in range(100):
        response = client.get("/api/v1/test-endpoint", headers=headers)
        responses.append(response)

    # Verify rate limit exceeded
    response = client.get("/api/v1/test-endpoint", headers=headers)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]