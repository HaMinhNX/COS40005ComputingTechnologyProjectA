import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_super_secret_key"
os.environ["GOOGLE_CLIENT_ID"] = "test_google_client_id"

from main import app
from database import Base, get_db

# Use in-memory SQLite for testing to ensure isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

VALID_PASSWORD = "SecurePass1!"   # meets all rules: 8+ chars, upper, lower, digit, special

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup and teardown the database once per test module."""
    app.dependency_overrides[get_db] = override_get_db
    print(f"DEBUG: Tables in Base.metadata: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_signup_success():
    # 1. Request OTP
    response = client.post(
        "/api/signup/request-otp",
        json={
            "username": "newtestuser",
            "email": "newtestuser@example.com",
            "password": VALID_PASSWORD,
            "full_name": "Test User",
            "role": "patient"
        }
    )
    assert response.status_code == 200, response.json()
    
    # Get the OTP from the in-memory DB directly using a separate session
    db = TestingSessionLocal()
    from models import OTPVerification
    otp_record = db.query(OTPVerification).filter(OTPVerification.email == "newtestuser@example.com").first()
    otp_code = otp_record.otp_code
    db.close()
    
    # 2. Verify OTP
    verify_response = client.post(
        "/api/signup/verify-otp",
        json={
            "email": "newtestuser@example.com",
            "otp_code": otp_code
        }
    )
    assert verify_response.status_code == 200, verify_response.json()
    data = verify_response.json()
    assert "access_token" in data
    assert data["username"] == "newtestuser"
    assert data["email"] == "newtestuser@example.com"


def test_signup_existing_username():
    response = client.post(
        "/api/signup/request-otp",
        json={
            "username": "newtestuser",
            "email": "differentemail@example.com",
            "password": VALID_PASSWORD,
            "full_name": "Test User Two",
            "role": "patient"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Tên đăng nhập đã tồn tại"

def test_signup_existing_email():
    response = client.post(
        "/api/signup/request-otp",
        json={
            "username": "differentusername",
            "email": "newtestuser@example.com",
            "password": VALID_PASSWORD,
            "full_name": "Test User Three",
            "role": "patient"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email đã được sử dụng"


def test_signup_weak_password_no_special_char():
    """Ensure passwords without special characters are rejected."""
    response = client.post(
        "/api/signup/request-otp",
        json={
            "username": "weakpwduser",
            "email": "weakpwd@example.com",
            "password": "Password123",   # no special char
            "full_name": "Weak Pwd",
            "role": "patient"
        }
    )
    assert response.status_code == 422, response.json()


def test_signup_weak_password_too_short():
    """Ensure passwords shorter than 8 chars are rejected."""
    response = client.post(
        "/api/signup/request-otp",
        json={
            "username": "weakpwduser2",
            "email": "weakpwd2@example.com",
            "password": "Ab1!",   # too short
            "full_name": "Weak Pwd Two",
            "role": "patient"
        }
    )
    assert response.status_code == 422, response.json()


def test_login_success():
    response = client.post(
        "/api/login",
        json={
            "username": "newtestuser@example.com",
            "password": VALID_PASSWORD
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "newtestuser"


def test_login_invalid_password():
    response = client.post(
        "/api/login",
        json={
            "username": "newtestuser@example.com",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Tên đăng nhập hoặc mật khẩu không đúng"


def test_login_nonexistent_user():
    response = client.post(
        "/api/login",
        json={
            "username": "nonexistent@example.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 401


# MOCK Google Login Test
def test_google_login_invalid_token():
    response = client.post(
        "/api/google",
        json={
            "credential": "invalid_jwt_token"
        }
    )
    # Expected to fail since google.oauth2.id_token.verify_oauth2_token will raise ValueError
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Google token"
