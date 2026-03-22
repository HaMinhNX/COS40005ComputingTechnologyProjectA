import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from database import Base, get_db
from models import User
from dependencies import get_current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup test DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_doctor_access_unassigned_patient():
    """Verify that a doctor can access an unassigned patient (Fix for 403 Forbidden)"""
    db = TestingSessionLocal()
    
    # 1. Create a doctor and a patient with NO relationship
    doctor_id = uuid4()
    patient_id = uuid4()
    
    doctor = User(
        user_id=doctor_id, 
        username="dr_unassigned_test", 
        email="dr_unassigned@test.com", 
        role="doctor", 
        password_hash="any"
    )
    patient = User(
        user_id=patient_id, 
        username="pt_unassigned_test", 
        email="pt_unassigned@test.com", 
        role="patient", 
        password_hash="any"
    )
    
    db.add(doctor)
    db.add(patient)
    db.commit()
    
    # 2. Mock current user as the doctor
    app.dependency_overrides[get_current_user] = lambda: doctor
    
    # 3. Try to access an endpoint that uses verify_patient_access
    # /api/medical-records/{patient_id} is a good candidate
    response = client.get(f"/api/medical-records/{patient_id}")
    
    # 4. Assert success (200 OK) instead of 403 Forbidden
    assert response.status_code == 200
    assert response.json()["patient_id"] == str(patient_id)
    
    # Clean up
    app.dependency_overrides.pop(get_current_user)
    db.close()

if __name__ == "__main__":
    # If run directly, run the test
    pytest.main([__file__])
