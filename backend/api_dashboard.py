from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from database import engine, Base
from dependencies import validate_environment
from routers import auth, patients, medical_records, assignments, schedules, messages, exercises, dashboard, doctors, plans, notifications

app = FastAPI(title="Medic1 Rehabilitation API", version="2.0")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
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

# Database initialization
Base.metadata.create_all(bind=engine)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


@app.on_event("startup")
async def startup_event():
    print("🚀 Medic1 API is starting up...")
    try:
        validate_environment()
        print("✅ Environment variables validated")
    except RuntimeError as e:
        print(f"❌ Startup Error: {e}")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Medic1 API is running",
        "version": "2.0"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
