from fastapi import FastAPI, Depends, Request, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging

from database import engine, Base, get_db
from dependencies import validate_environment, get_current_user
from models import User
from routers import auth, patients, medical_records, assignments, schedules, messages, exercises, dashboard, doctors, plans, notifications, ai_chat, wearable

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Medic1 API is starting up...")
    try:
        validate_environment()
        print(" Environment variables validated")
    except RuntimeError as e:
        print(f" Startup Error: {e}")
    yield

# Initialize database tables on module load (Supported by Vercel cold starts)
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables synchronized")
except Exception as e:
    print(f" Database sync skipped or failed: {e}")

app = FastAPI(title="Medic1 Rehabilitation API", version="2.1", lifespan=lifespan)

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "https://medic1-le-minh.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    from fastapi.encoders import jsonable_encoder
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )

from fastapi import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )

@app.get("/")
@app.get("/api")
@app.get("/api/")
async def root():
    return {
        "status": "ok",
        "message": "Medic1 API is running",
        "version": "2.1"
    }

# Include Routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(medical_records.router)
app.include_router(assignments.router)
app.include_router(schedules.router)
app.include_router(messages.router)
app.include_router(exercises.router)
app.include_router(dashboard.router)
app.include_router(doctors.router)
app.include_router(plans.router)
app.include_router(notifications.router)
app.include_router(ai_chat.router)
app.include_router(wearable.router)

# === Legacy/Compatibility Endpoints ===
@app.get("/api/doctor-id")
async def get_doctor_id_legacy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Smart endpoint for doctor ID.
    1. If user is patient, try to find their assigned doctor from WeekPlans, Assignments, or Schedules.
    2. Fallback to first doctor if no relationship found.
    """
    from models import User, WeekPlan, Assignment, Schedule
    
    doctor_id = None
    
    if current_user.role == 'patient':
        # 1. Check active WeekPlan
        plan = db.query(WeekPlan).filter(
            WeekPlan.patient_id == current_user.user_id,
            WeekPlan.status == 'active'
        ).order_by(WeekPlan.created_at.desc()).first()
        if plan:
            doctor_id = plan.doctor_id
            
        # 2. If no plan, check latest Assignment
        if not doctor_id:
            assign = db.query(Assignment).filter(
                Assignment.patient_id == current_user.user_id
            ).order_by(Assignment.created_at.desc()).first()
            if assign:
                doctor_id = assign.doctor_id

        # 3. If no assignment, check latest Schedule
        if not doctor_id:
            sched = db.query(Schedule).filter(
                Schedule.patient_id == current_user.user_id
            ).order_by(Schedule.created_at.desc()).first()
            if sched:
                doctor_id = sched.doctor_id

    # 4. Fallback: Return first doctor found (Demo mode)
    if not doctor_id:
        doctor = db.query(User).filter(User.role == 'doctor').first()
        if doctor:
            doctor_id = doctor.user_id
            
    return {"doctor_id": str(doctor_id) if doctor_id else None}

# Proper authenticated endpoint
from dependencies import get_current_doctor
from models import User

@app.get("/api/me/doctor-id")
async def get_authenticated_doctor_id(current_user: User = Depends(get_current_doctor)):
    """Returns the authenticated doctor's ID"""
    return {"doctor_id": str(current_user.user_id)}


# === Auto Mail Endpoint ===
from pydantic import BaseModel as PydanticBaseModel

class SendReportRequest(PydanticBaseModel):
    receiver_email: str
    patient_name: str

@app.post("/api/send-report-email")
async def send_report_email(req: SendReportRequest):
    from auto_mail import send_health_email
    try:
        success = send_health_email(receiver=req.receiver_email, name=req.patient_name)
        if success:
            return {"success": True, "message": f"Báo cáo đã được gửi tới {req.receiver_email}"}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Gửi email thất bại. Kiểm tra cấu hình SMTP."}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Lỗi: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
