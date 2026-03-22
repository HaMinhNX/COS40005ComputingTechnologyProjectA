import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables BEFORE importing main to avoid connecting to production DB
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from database import Base, get_db
from models import User, MedicalRecord
from dependencies import get_current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import routers.ai_chat

# Ensure GEMINI_API_KEY is set for tests
routers.ai_chat.GEMINI_API_KEY = "test_key"

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

def test_ai_chat_streaming_success():
    # Create test data
    db = TestingSessionLocal()
    doctor_id = uuid4()
    patient_id = uuid4()
    
    doctor = User(user_id=doctor_id, username="dr_ai_test", email="dr_ai@test.com", role="doctor", password_hash="...")
    patient = User(user_id=patient_id, username="pt_ai_test", email="pt_ai@test.com", role="patient", password_hash="...")
    
    medical_record = MedicalRecord(patient_id=patient_id, diagnosis="Test Diagnosis", symptoms="Test Symptoms")
    
    db.add(doctor)
    db.add(patient)
    db.add(medical_record)
    db.add(doctor)
    db.add(patient)
    db.add(medical_record)
    db.commit()
    # Don't close session here to avoid DetachedInstanceError when accessed by FastAPI
    # db.close() 

    # Mock dependencies and Gemini
    app.dependency_overrides[get_current_user] = lambda: doctor
    
    with patch("dependencies.verify_patient_access", return_value=patient):
        with patch("os.getenv", return_value="test_key"):
            with patch("routers.ai_chat.genai.GenerativeModel") as mock_model:
                mock_instance = mock_model.return_value
                
                # Mock streaming response
                chunk1 = MagicMock()
                chunk1.text = "Chào"
                chunk2 = MagicMock()
                chunk2.text = " bạn"
                
                mock_instance.generate_content.return_value = [chunk1, chunk2]

                response = client.post(
                    "/api/ai/chat",
                    json={"patient_id": str(patient_id), "message": "Chào AI"}
                )
                
                assert response.status_code == 200
                # Check for SSE format
                assert "data: " in response.text
                assert "Chào" in response.text
                assert "bạn" in response.text
                assert "[DONE]" in response.text
    
    # Clean up overrides
    app.dependency_overrides.pop(get_current_user)
