import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User, OTPVerification
from auth import get_password_hash

client = TestClient(app)

def test_flow():
    db = SessionLocal()
    
    # Clean up test user if exists
    test_email = "test_forgot@example.com"
    db.query(OTPVerification).filter(OTPVerification.email == test_email).delete()
    db.query(User).filter(User.email == test_email).delete()
    db.commit()

    # Create test user
    test_user = User(
        username="test_forgot",
        email=test_email,
        password_hash=get_password_hash("OldPassword123!"),
        full_name="Test Forgot",
        role="patient"
    )
    db.add(test_user)
    db.commit()

    print("--- Starting Test Flow ---")

    # Request OTP
    response = client.post("/api/forgot-password/request-otp", json={"email": test_email})
    assert response.status_code == 200, f"Failed request otp: {response.text}"
    print("1. Request OTP Success:", response.json())

    # Get OTP from DB
    otp_record = db.query(OTPVerification).filter(OTPVerification.email == test_email).first()
    assert otp_record is not None
    otp_code = otp_record.otp_code
    print("2. Got OTP from DB:", otp_code)

    # Verify OTP
    response = client.post("/api/forgot-password/verify-otp", json={"email": test_email, "otp_code": otp_code})
    assert response.status_code == 200, f"Failed verify otp: {response.text}"
    print("3. Verify OTP Success:", response.json())

    # Reset Password
    new_password = "NewPassword123!"
    response = client.post("/api/forgot-password/reset", json={
        "email": test_email,
        "otp_code": otp_code,
        "new_password": new_password
    })
    assert response.status_code == 200, f"Failed reset password: {response.text}"
    print("4. Reset Password Success:", response.json())

    # Verify DB updated
    updated_user = db.query(User).filter(User.email == test_email).first()
    from auth import verify_password
    assert verify_password(new_password, updated_user.password_hash), "Password did not update correctly!"
    print("5. Password correctly updated in DB!")

    # Verify OTP record deleted
    otp_record_after = db.query(OTPVerification).filter(OTPVerification.email == test_email).first()
    assert otp_record_after is None, "OTP record should be deleted!"
    print("6. OTP record deleted!")

    # Test bad OTP
    response = client.post("/api/forgot-password/verify-otp", json={"email": test_email, "otp_code": "000000"})
    assert response.status_code == 400
    print("7. Invalid OTP handled correctly")

    # Cleanup
    db.delete(updated_user)
    db.commit()
    print("--- Test DB cleanup done ---")
    print("All tests passed.")

if __name__ == "__main__":
    test_flow()
