from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import verify_password, get_password_hash, create_access_token
from dependencies import get_current_user
from schemas import UserLogin, UserWithToken, UserResponse, GoogleLogin, ForgotPasswordRequest, VerifyForgotPasswordOTP, ResetPassword
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import json
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, field_validator
from models import OTPVerification
from enums import DoctorApprovalStatus, UserRole
from models import DoctorVerification


router = APIRouter(
    prefix="/api",
    tags=["auth"]
)


def upload_certificate_to_cloudinary(file: UploadFile) -> tuple[str, str]:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not cloud_name or not api_key or not api_secret:
        raise HTTPException(status_code=500, detail="Cloudinary configuration is missing")

    file_bytes = file.file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded certificate file is empty")

    try:
        import cloudinary
        import cloudinary.uploader
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloudinary package not installed: {exc}") from exc

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )

    content_type = (file.content_type or "").lower()
    resource_type = "raw" if content_type == "application/pdf" else "image"
    original_name = (file.filename or "").strip().lower()
    extension = ""
    if "." in original_name:
        extension = original_name.rsplit(".", 1)[-1]
    if not extension:
        extension = "pdf" if content_type == "application/pdf" else "png"
    # Keep extension in public_id so downloaded file has a proper suffix.
    public_id = f"doctor_{uuid.uuid4()}.{extension}"

    try:
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            resource_type=resource_type,
            folder="doctor-certificates",
            public_id=public_id,
            overwrite=False
        )
        secure_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        if not secure_url or not public_id:
            raise HTTPException(status_code=500, detail="Failed to upload certificate")
        return secure_url, public_id
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to upload certificate: {exc}") from exc

@router.post("/login", response_model=UserWithToken)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login - Returns user info with token"""
    username = data.username
    password = data.password
    
    user = db.query(User).filter(User.email == username).first()
    
    if user:
        print(f"DEBUG LOGIN: Found user for email={username}, role={user.role}")
        # Check password (hashed only - legacy plain text support removed)
        result = verify_password(password, user.password_hash)
        print(f"DEBUG LOGIN: verify_password result={result}")
        if result:
            if user.role == UserRole.DOCTOR.value:
                if user.approval_status == DoctorApprovalStatus.PENDING.value:
                    raise HTTPException(status_code=403, detail="Doctor account is pending admin approval")
                if user.approval_status == DoctorApprovalStatus.REJECTED.value:
                    raise HTTPException(status_code=403, detail="Doctor account was rejected by admin")

            # Create real JWT token
            access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
            print(f"DEBUG LOGIN: Created token for user_id={user.user_id}")
            
            return {
                "access_token": access_token,
                "token": access_token, # Backward compatibility
                "user_id": str(user.user_id),
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name,
                "name": user.full_name,
                "email": user.email or "",
                "created_at": user.created_at
            }
    else:
        print(f"DEBUG LOGIN: User NOT found for email={username}")
    
    raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không đúng")


@router.post("/signup/doctor-with-certificate")
async def signup_doctor_with_certificate(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    certificate: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    from schemas.user import validate_password_strength

    validate_password_strength(password)

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    allowed_content_types = {"image/jpeg", "image/png", "application/pdf"}
    if certificate.content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail="Certificate file must be JPG, PNG, or PDF")

    certificate_url, public_id = upload_certificate_to_cloudinary(certificate)
    hashed_password = get_password_hash(password)

    try:
        new_doctor = User(
            username=username,
            password_hash=hashed_password,
            full_name=full_name,
            email=email,
            role=UserRole.DOCTOR.value,
            approval_status=DoctorApprovalStatus.PENDING.value
        )
        db.add(new_doctor)
        db.flush()

        verification = DoctorVerification(
            doctor_id=new_doctor.user_id,
            certificate_url=certificate_url,
            certificate_public_id=public_id
        )
        db.add(verification)
        db.commit()
        db.refresh(new_doctor)

        return {
            "message": "Doctor registration submitted and waiting for admin approval",
            "doctor_id": str(new_doctor.user_id),
            "approval_status": new_doctor.approval_status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo tài khoản bác sĩ: {str(e)}")

class OTPRequestSchema(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    role: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        from schemas.user import validate_password_strength
        return validate_password_strength(v)

class OTPVerifySchema(BaseModel):
    email: str
    otp_code: str

def send_otp_email(recipient: str, otp_code: str):
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    if not sender or not password:
        print(f"SMTP config missing. Fake sent OTP to {recipient}: {otp_code}")
        return

    msg = MIMEMultipart()
    msg['From'] = f"HaminG <{sender}>"
    msg['To'] = recipient
    msg['Subject'] = "Mã xác nhận đăng ký HaminG"

    body = f"Chào bạn,\n\nMã xác nhận (OTP) của bạn là: {otp_code}\nMã này sẽ hết hạn trong 15 phút.\n\nTrân trọng,\nĐội ngũ HaminG"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # server.starttls() # Not needed for SSL
        if sender and password:
            server.login(sender, password)
        else:
            print("ERROR: SMTP credentials missing")
            return
        server.send_message(msg)
        server.quit()
        print(f"DEBUG: Sent OTP to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_forgot_password_email(recipient: str, otp_code: str):
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    if not sender or not password:
        print(f"SMTP config missing. Fake sent forgot password OTP to {recipient}: {otp_code}")
        return

    msg = MIMEMultipart()
    msg['From'] = f"HaminG <{sender}>"
    msg['To'] = recipient
    msg['Subject'] = "Mã xác nhận quên mật khẩu HaminG"

    body = f"Chào bạn,\n\nMã xác nhận (OTP) để đặt lại mật khẩu của bạn là: {otp_code}\nMã này sẽ hết hạn trong 15 phút.\nNếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.\n\nTrân trọng,\nĐội ngũ HaminG"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # server.starttls() # Not needed for SSL
        if sender and password:
            server.login(sender, password)
        else:
            print("ERROR: SMTP credentials missing")
            return
        server.send_message(msg)
        server.quit()
        print(f"DEBUG: Sent forgot password OTP to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@router.post("/signup/request-otp")
async def request_otp(data: OTPRequestSchema, db: Session = Depends(get_db)):
    """Request OTP for signup"""
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    otp_code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Use timezone-naive datetime for compatibility with PostgreSQL TIMESTAMP WITHOUT TIME ZONE (if needed)
    # Actually, models.py says DateTime(timezone=True), so timezone-aware is perfect

    existing = db.query(OTPVerification).filter(OTPVerification.email == data.email).first()
    if existing:
        existing.otp_code = otp_code
        existing.expires_at = expires_at
        existing.user_data = json.dumps(data.model_dump())
    else:
        new_verify = OTPVerification(
            email=data.email,
            otp_code=otp_code,
            expires_at=expires_at,
            user_data=json.dumps(data.model_dump())
        )
        db.add(new_verify)
    
    db.commit()
    send_otp_email(data.email, otp_code)
    
    return {"message": "Mã OTP đã được gửi đến email của bạn."}

@router.post("/signup/verify-otp", response_model=UserWithToken)
async def verify_otp(data: OTPVerifySchema, db: Session = Depends(get_db)):
    """Verify OTP and complete signup"""
    verify_record = db.query(OTPVerification).filter(OTPVerification.email == data.email).first()
    if not verify_record:
        raise HTTPException(status_code=400, detail="Không tìm thấy yêu cầu xác nhận cho email này")
        
    if verify_record.otp_code != data.otp_code:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác")
        
    # Python datetime.now(timezone.utc) comparison with a timezone-aware datetime from SQLAlchemy
    # sometimes needs to ensure both are aware. SQLAlchemy returns aware because DateTime(timezone=True).
    now = datetime.now(timezone.utc)
    # Hack to avoid naive vs aware error if DB returns naive:
    expires = verify_record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
        
    if expires < now:
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
        
    user_data = json.loads(verify_record.user_data)
    hashed_password = get_password_hash(user_data['password'])
    
    try:
        new_user = User(
            username=user_data['username'],
            password_hash=hashed_password,
            full_name=user_data['full_name'],
            email=user_data['email'],
            role=user_data['role']
        )
        db.add(new_user)
        db.delete(verify_record)
        db.commit()
        db.refresh(new_user)
        
        access_token = create_access_token(data={"sub": str(new_user.user_id), "role": new_user.role})
        
        return {
            "access_token": access_token,
            "token": access_token,
            "user_id": str(new_user.user_id),
            "username": new_user.username,
            "role": new_user.role,
            "full_name": new_user.full_name,
            "name": new_user.full_name,
            "email": new_user.email,
            "created_at": new_user.created_at
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo tài khoản: {str(e)}")

@router.post("/forgot-password/request-otp")
async def forgot_password_request_otp(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request OTP for forgot password"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Không tìm thấy tài khoản với email này")
        
    otp_code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    existing = db.query(OTPVerification).filter(OTPVerification.email == data.email).first()
    if existing:
        existing.otp_code = otp_code
        existing.expires_at = expires_at
        existing.user_data = json.dumps({"reason": "forgot_password"})
    else:
        new_verify = OTPVerification(
            email=data.email,
            otp_code=otp_code,
            expires_at=expires_at,
            user_data=json.dumps({"reason": "forgot_password"})
        )
        db.add(new_verify)
    
    db.commit()
    send_forgot_password_email(data.email, otp_code)
    
    return {"message": "Mã OTP đặt lại mật khẩu đã được gửi đến email của bạn."}

@router.post("/forgot-password/verify-otp")
async def forgot_password_verify_otp(data: VerifyForgotPasswordOTP, db: Session = Depends(get_db)):
    """Verify OTP for forgot password"""
    verify_record = db.query(OTPVerification).filter(OTPVerification.email == data.email).first()
    if not verify_record:
        raise HTTPException(status_code=400, detail="Không tìm thấy yêu cầu xác nhận cho email này")
        
    if verify_record.otp_code != data.otp_code:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác")
        
    now = datetime.now(timezone.utc)
    expires = verify_record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
        
    if expires < now:
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
        
    # Valid OTP
    return {"message": "Mã OTP hợp lệ"}

@router.post("/forgot-password/reset")
async def forgot_password_reset(data: ResetPassword, db: Session = Depends(get_db)):
    """Reset password after OTP verification"""
    verify_record = db.query(OTPVerification).filter(OTPVerification.email == data.email).first()
    if not verify_record:
        raise HTTPException(status_code=400, detail="Không tìm thấy yêu cầu xác nhận cho email này")
        
    if verify_record.otp_code != data.otp_code:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác hoặc đã hết hạn")
        
    now = datetime.now(timezone.utc)
    expires = verify_record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
        
    if expires < now:
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
        
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Không tìm thấy người dùng")
        
    # Update password
    hashed_password = get_password_hash(data.new_password)
    user.password_hash = hashed_password
    
    # Delete OTP record
    db.delete(verify_record)
    db.commit()
    
    return {"message": "Đặt lại mật khẩu thành công. Bạn có thể đăng nhập với mật khẩu mới."}

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

@router.post("/google", response_model=UserWithToken)
async def google_login(data: GoogleLogin, db: Session = Depends(get_db)):
    """Google Login - Authenticates using Google JWT Token"""
    try:
        # For production, ensure GOOGLE_CLIENT_ID is set
        # verify the Google JWT token
        idinfo = id_token.verify_oauth2_token(
            data.credential, google_requests.Request(), GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )

        email = idinfo['email']
        name = idinfo.get('name', 'Google User')
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
                
            hashed_password = get_password_hash(str(uuid.uuid4())) 
            user = User(
                username=username,
                password_hash=hashed_password,
                full_name=name,
                email=email,
                role='patient'
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
        
        return {
            "access_token": access_token,
            "token": access_token,
            "user_id": str(user.user_id),
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "name": user.full_name,
            "email": user.email,
            "created_at": user.created_at
        }
    except ValueError:
        # Ignore client ID mismatch if needed during dev, but throw auth error ideally
        raise HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user details"""
    return current_user
