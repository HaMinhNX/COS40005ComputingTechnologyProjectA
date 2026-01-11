from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Security: SECRET_KEY must be set in environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "your_super_secret_key_change_this_in_production":
    raise RuntimeError(
        "SECRET_KEY environment variable must be set to a secure value. "
        "Please update your .env file with a strong, unique secret key."
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
