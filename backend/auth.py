from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
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
if ALGORITHM and ALGORITHM.startswith("ALGORITHM="):
    ALGORITHM = ALGORITHM.replace("ALGORITHM=", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password == hashed_password:
        return True
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    print(f"DEBUG IN HASH: {repr(password)}, type={type(password)}, len={len(password)}")
    encoded = password.encode('utf-8')
    print(f"DEBUG IN HASH encoded: len={len(encoded)}")
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # Use simple string slicing with explicit type safety for the IDE
        token_preview = str(token)[:10] if token else "None"
        print(f"DEBUG AUTH: JWTError: {e} for token: {token_preview}...")
        return None

