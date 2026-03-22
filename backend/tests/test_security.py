import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_sql_injection_attempt_login(client):
    # Try SQL injection in email field
    payload = {
        "email": "admin' OR '1'='1",
        "password": "password123"
    }
    response = client.post("/api/login", json=payload)
    
    # The application should safely reject this as unauthorized (401) or invalid format (422)
    # rather than failing with a 500 DB error
    assert response.status_code in [401, 422]

def test_cors_headers(client):
    # Test if CORS is configured to avoid arbitrary cross-origin issues
    response = client.options("/api/login", headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "POST"})
    
    # Typically, the response should have CORS headers but maybe restricted if explicit
    # Or at least not fail. We'll just verify the app doesn't crash on preflight.
    assert response.status_code in [200, 400]
