import pytest
from fastapi.testclient import TestClient
import time
from main import app
from database import Base, engine, TestingSessionLocal

@pytest.fixture(scope="module")
def client():
    # Performance test uses the same app, could use real db or test db
    with TestClient(app) as c:
        yield c

def test_patients_endpoint_performance(client):
    start = time.time()
    response = client.get("/api/patients")
    end = time.time()
    
    # In unauthenticated state, it should return 401 fast
    assert response.status_code == 401
    assert (end - start) < 0.5  # Under 500ms

def test_auth_login_performance(client):
    start = time.time()
    response = client.post("/api/login", json={"email": "test@test.com", "password": "wrong"})
    end = time.time()
    
    # Should be fast even for failed login
    assert response.status_code == 401
    assert (end - start) < 1.0  # Password hashing makes it slightly slower
