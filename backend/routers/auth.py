from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import verify_password, get_password_hash, create_access_token
from dependencies import get_current_user
from schemas import UserLogin, UserCreate, UserWithToken, UserResponse

router = APIRouter(
    prefix="/api",
    tags=["auth"]
)

@router.post("/login", response_model=UserWithToken)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login - Returns user info with token"""
    username = data.username
    password = data.password
    
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        # Check password (hashed only - legacy plain text support removed)
        if verify_password(password, user.password_hash):
            # Create real JWT token
            access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
            
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
    
    raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không đúng")

@router.post("/signup", response_model=UserWithToken)
async def signup(data: UserCreate, db: Session = Depends(get_db)):
    """Signup - Create new user account"""
    username = data.username
    password = data.password
    full_name = data.full_name
    email = data.email
    role = data.role.value if hasattr(data.role, 'value') else data.role
    
    if not username or not password or not full_name or not email:
        raise HTTPException(status_code=400, detail="Thiếu thông tin bắt buộc")
    
    # Check existence
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    if db.query(User).filter(User.full_name == full_name).first():
         raise HTTPException(status_code=400, detail="Tên này đã được sử dụng")
    
    try:
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            password_hash=hashed_password,
            full_name=full_name,
            email=email,
            role=role
        )
        db.add(new_user)
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
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo tài khoản: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user details"""
    return current_user
