import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from models import User, MedicalRecord
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

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_ai_chat_streaming_success():
    # Create test data
    db = TestingSessionLocal()
    doctor_id = uuid4()
    patient_id = uuid4()
    
    doctor = User(user_id=doctor_id, username="dr_ai_test", email="dr_ai@test.com", role="doctor", hashed_password="...")
    patient = User(user_id=patient_id, username="pt_ai_test", email="pt_ai@test.com", role="patient", hashed_password="...")
    
    medical_record = MedicalRecord(patient_id=patient_id, diagnosis="Test Diagnosis", symptoms="Test Symptoms")
    
    db.add(doctor)
    db.add(patient)
    db.add(medical_record)
    db.commit()
    db.close()

    # Mock dependencies and Gemini
    with patch("dependencies.get_current_user", return_value=doctor):
        with patch("dependencies.verify_patient_access", return_value=patient):
            with patch("os.getenv", return_value="test_key"):
                with patch("google.generativeai.GenerativeModel") as mock_model:
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
