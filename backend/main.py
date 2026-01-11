from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional
import time
import atexit
import uuid

# === BƯỚC 1: KIỂM TRA IMPORT & DB KHI KHỞI ĐỘNG ===
print("⚠️  WARNING: main.py is DEPRECATED. Please use api_dashboard.py on port 8001.")
print("Đang khởi động ứng dụng...")


from datetime import datetime

# Import logic
try:
    from exercise_logic import (
        AngleCalculator, 
        Landmark, 
        EXERCISE_COUNTER, 
        SquatState, 
        BicepCurlState,
        ShoulderFlexionState,
        KneeRaiseState
    )
    print("exercise_logic: OK")
except ImportError as e:
    print("exercise_logic: THẤT BẠI - Kiểm tra file exercise_logic.py")
    raise e

app = FastAPI()

# === DATABASE SETUP ===
from database import engine, SessionLocal, get_db
from models import Base, ExerciseLogSimple, User
from sqlalchemy.orm import Session
from sqlalchemy import text, func

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Check DB connection
_db_available = False
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Kết nối Neon DB: THÀNH CÔNG")
    _db_available = True
except Exception as e:
    print(f"⚠️  Kết nối Neon DB: THẤT BẠI - {e}")
    print("⚠️  Ứng dụng sẽ chạy KHÔNG CÓ DATABASE (chỉ xử lý camera)")
    _db_available = False

# === GHI LOG ===
def log_to_postgres(data: dict):
    if not _db_available:
        return
    
    db = SessionLocal()
    try:
        date_obj = datetime.strptime(data['date'], "%d/%m/%Y").date()
        
        new_log = ExerciseLogSimple(
            user_id=uuid.UUID(data['user_id']) if data.get('user_id') else None,
            date=date_obj,
            exercise_type=data['exercise_type'],
            feedback=data['feedback'] if data['feedback'] else None,
            rep_count=data['rep_count'],
            session_duration=round(float(data['session_duration']), 2)
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB ERROR] Insert failed: {e}")
    finally:
        db.close()

# Đóng kết nối (SQLAlchemy handles pool, but we can dispose engine if needed)
def close_db():
    engine.dispose()
    print("Đã đóng connection pool PostgreSQL.")
atexit.register(close_db)

# === CORS ===
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

# === VALIDATION ERROR HANDLER (for debugging 422 errors) ===
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(" VALIDATION ERROR DETECTED!")
    print(f"Request URL: {request.url}")
    print(f"Request method: {request.method}")
    
    # Try to get request body
    try:
        body = await request.body()
        print(f"Request body (first 500 chars): {body[:500]}")
    except:
        print("Could not read request body")
    
    print(f"\nValidation errors:")
    for error in exc.errors():
        print(f"  - Field: {error['loc']}")
        print(f"    Type: {error['type']}")
        print(f"    Message: {error['msg']}")
        if 'ctx' in error:
            print(f"    Context: {error['ctx']}")
    print("="*60 + "\n")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc)
        }
    )

# === Database Availability Decorator ===
from functools import wraps

def requires_database(func):
    """Decorator to check if database is available before executing endpoint"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not _db_available:
            raise HTTPException(
                status_code=503, 
                detail="Database không khả dụng. Chỉ có thể sử dụng chức năng camera."
            )
        return await func(*args, **kwargs)
    return wrapper

# === Pydantic Models ===
# === Pydantic Models ===
class LandmarkData(BaseModel):
    x: float
    y: float
    z: float = 0.0
    visibility: float = 0.0

class ProcessRequest(BaseModel):
    landmarks: List[LandmarkData]
    current_exercise: str
    user_id: Optional[str] = None # UUID string

class ProcessResponse(BaseModel):
    squat_count: int
    curl_count: int
    shoulder_flexion_count: int
    knee_raise_count: int
    total_reps: int
    squat_state_name: str
    curl_state_name: str
    shoulder_flexion_state_name: str
    knee_raise_state_name: str
    feedback: str

# === Helper ===
def get_state_name(state_class, state_value):
    state_dict = {v: k for k, v in state_class.__dict__.items() if isinstance(v, int)}
    return state_dict.get(state_value, "UNKNOWN")

# === Calculate Angles ===
def calculate_all_angles(landmarks: List[LandmarkData]) -> Dict[str, Any]:
    lm_objects = [Landmark(lm.x, lm.y, lm.z, lm.visibility) for lm in landmarks]
    if len(lm_objects) < 33:
        return {'error': 'Insufficient landmarks'}

    left_shoulder = lm_objects[11]; right_shoulder = lm_objects[12]
    left_elbow = lm_objects[13]; right_elbow = lm_objects[14]
    left_wrist = lm_objects[15]; right_wrist = lm_objects[16]
    left_hip = lm_objects[23]; right_hip = lm_objects[24]
    left_knee = lm_objects[25]; right_knee = lm_objects[26]
    left_ankle = lm_objects[27]; right_ankle = lm_objects[28]

    left_bicep_angle = AngleCalculator.calculate_bicep_angle(left_shoulder, left_elbow, left_wrist, 0.7)
    right_bicep_angle = AngleCalculator.calculate_bicep_angle(right_shoulder, right_elbow, right_wrist, 0.7)
    elbow_torso_result = AngleCalculator.calculate_elbow_torso_angle(left_hip, left_shoulder, left_elbow, right_hip, right_shoulder, right_elbow, 0.7)
    hip_shoulder_angle = AngleCalculator.calculate_hip_shoulder_angle(left_hip, left_shoulder, 0.7)
    knee_angle_avg = AngleCalculator.calculate_average_knee_angle(left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle, 0.7)
    left_knee_angle = AngleCalculator.calculate_knee_angle(left_hip, left_knee, left_ankle, 0.7)
    right_knee_angle = AngleCalculator.calculate_knee_angle(right_hip, right_knee, right_ankle, 0.7)

    left_back_angle = AngleCalculator.calculate_hip_shoulder_angle(left_hip, left_shoulder, 0.7)
    right_back_angle = AngleCalculator.calculate_hip_shoulder_angle(right_hip, right_shoulder, 0.7)
    back_angle = (left_back_angle + right_back_angle) / 2 if left_back_angle and right_back_angle else (left_back_angle or right_back_angle)

    left_flexion_angle = AngleCalculator.calculate_shoulder_flexion_angle(left_hip, left_shoulder, left_wrist, 0.7)
    right_flexion_angle = AngleCalculator.calculate_shoulder_flexion_angle(right_hip, right_shoulder, right_wrist, 0.7)
    left_elbow_angle = AngleCalculator.calculate_elbow_bend_angle(left_shoulder, left_elbow, left_wrist, 0.7)
    right_elbow_angle = AngleCalculator.calculate_elbow_bend_angle(right_shoulder, right_elbow, right_wrist, 0.7)

    return {
        'left_bicep_angle': left_bicep_angle, 'right_bicep_angle': right_bicep_angle,
        'elbow_torso_result': elbow_torso_result, 'hip_shoulder_angle': hip_shoulder_angle,
        'knee_angle_avg': knee_angle_avg, 'left_knee_angle': left_knee_angle, 'right_knee_angle': right_knee_angle,
        'back_angle': back_angle, 'left_flexion_angle': left_flexion_angle, 'right_flexion_angle': right_flexion_angle,
        'left_elbow_angle': left_elbow_angle, 'right_elbow_angle': right_elbow_angle,
        'landmarks': lm_objects
    }

# === API Endpoints ===
@app.post("/select_exercise")
async def select_exercise(exercise_name: str):
    EXERCISE_COUNTER.reset_state(exercise_name)
    exercise_key = exercise_name.replace('-', '_')
    setattr(EXERCISE_COUNTER, f"{exercise_key}_start_time", time.time())
    prev_reps[exercise_name] = 0
    return {"message": f"State reset for {exercise_name}"}

prev_reps: Dict[str, int] = {}

# === Feedback Stabilization ===
class FeedbackState:
    def __init__(self):
        self.last_feedback = ""
        self.last_feedback_time = 0
        self.display_duration = 2.0  # Seconds to show feedback
        self.priority_feedback = None # (text, expiry_time)

    def get_display_feedback(self, new_feedback: str, state_guidance: str) -> str:
        now = time.time()
        
        # 1. Priority Feedback (Corrections/Errors) - Sticky
        if new_feedback:
            # New correction comes in, update priority
            self.priority_feedback = (new_feedback, now + self.display_duration)
            return new_feedback
        
        # 2. Check if existing priority feedback is still valid
        if self.priority_feedback:
            text, expiry = self.priority_feedback
            if now < expiry:
                return text
            else:
                self.priority_feedback = None # Expired

        # 3. State Guidance (Instruction) - Only if no priority feedback
        return state_guidance

FEEDBACK_STATE = FeedbackState()


@app.post("/process_landmarks", response_model=ProcessResponse)
async def process_landmarks_api(request: ProcessRequest):
    try:
        if not request.landmarks:
            raise HTTPException(status_code=400, detail="No landmarks provided")

        angles = calculate_all_angles(request.landmarks)
        if 'error' in angles:
            raise HTTPException(status_code=400, detail=angles['error'])

        lm_objects = angles['landmarks']
        left_shoulder = lm_objects[11]; right_shoulder = lm_objects[12]
        left_elbow = lm_objects[13]; right_elbow = lm_objects[14]
        left_wrist = lm_objects[15]; right_wrist = lm_objects[16]
        left_hip = lm_objects[23]; right_hip = lm_objects[24]
        left_knee = lm_objects[25]; right_knee = lm_objects[26]
        left_ankle = lm_objects[27]; right_ankle = lm_objects[28]

        if request.current_exercise not in prev_reps:
            prev_reps[request.current_exercise] = 0

        # Feedback manager
        if request.current_exercise == 'squat':
            old_rep = EXERCISE_COUNTER.squat_counter
            feedback_manager = EXERCISE_COUNTER.squat_feedback_manager
        elif request.current_exercise == 'bicep-curl':
            old_rep = EXERCISE_COUNTER.curl_counter
            feedback_manager = EXERCISE_COUNTER.bicep_curl_feedback_manager
        elif request.current_exercise == 'shoulder-flexion':
            old_rep = EXERCISE_COUNTER.shoulder_flexion_counter
            feedback_manager = EXERCISE_COUNTER.shoulder_flexion_feedback_manager
        elif request.current_exercise == 'knee-raise':
            old_rep = EXERCISE_COUNTER.knee_raise_counter
            feedback_manager = EXERCISE_COUNTER.knee_raise_feedback_manager
        else:
            old_rep = 0
            feedback_manager = None

        # Process
        if request.current_exercise == 'bicep-curl':
            state, _ = EXERCISE_COUNTER.process_bicep_curl(
                left_shoulder=left_shoulder, left_elbow=left_elbow, left_wrist=left_wrist, left_hip=left_hip,
                right_shoulder=right_shoulder, right_elbow=right_elbow, right_wrist=right_wrist, right_hip=right_hip,
                left_bicep_angle=angles['left_bicep_angle'], right_bicep_angle=angles['right_bicep_angle'],
                elbow_torso_result=angles['elbow_torso_result'], hip_shoulder_angle=angles['hip_shoulder_angle']
            )
            curl_state_name = get_state_name(BicepCurlState, state)
        elif request.current_exercise == 'squat':
            state, _ = EXERCISE_COUNTER.process_squat(
                knee_angle=angles['knee_angle_avg'], back_angle=angles['back_angle'],
                left_hip=left_hip, right_hip=right_hip, left_knee=left_knee, right_knee=right_knee,
                left_ankle=left_ankle, right_ankle=right_ankle,
                left_shoulder=left_shoulder, right_shoulder=right_shoulder
            )
            squat_state_name = get_state_name(SquatState, state)
        elif request.current_exercise == 'shoulder-flexion':
            state, _ = EXERCISE_COUNTER.process_shoulder_flexion(
                left_hip=left_hip, left_shoulder=left_shoulder, left_elbow=left_elbow, left_wrist=left_wrist,
                right_hip=right_hip, right_shoulder=right_shoulder, right_elbow=right_elbow, right_wrist=right_wrist,
                left_flexion_angle=angles['left_flexion_angle'], right_flexion_angle=angles['right_flexion_angle'],
                left_elbow_angle=angles['left_elbow_angle'], right_elbow_angle=angles['right_elbow_angle'],
                hip_shoulder_angle=angles['hip_shoulder_angle']
            )
            shoulder_flexion_state_name = get_state_name(ShoulderFlexionState, state)
        elif request.current_exercise == 'knee-raise':
            state, _ = EXERCISE_COUNTER.process_knee_raise(
                left_hip=left_hip, left_knee=left_knee, left_ankle=left_ankle,
                right_hip=right_hip, right_knee=right_knee, right_ankle=right_ankle,
                left_shoulder=left_shoulder, left_wrist=left_wrist,
                right_shoulder=right_shoulder, right_wrist=right_wrist,
                left_knee_angle=angles['left_knee_angle'], right_knee_angle=angles['right_knee_angle'],
                left_flexion_angle=angles['left_flexion_angle'], right_flexion_angle=angles['right_flexion_angle'],
                hip_shoulder_angle=angles['hip_shoulder_angle']
            )
            knee_raise_state_name = get_state_name(KneeRaiseState, state)
        else:
            state = None

        # State names
        squat_state_name = get_state_name(SquatState, EXERCISE_COUNTER.squat_state)
        curl_state_name = get_state_name(BicepCurlState, EXERCISE_COUNTER.bicep_curl_state)
        shoulder_flexion_state_name = get_state_name(ShoulderFlexionState, EXERCISE_COUNTER.shoulder_flexion_state)
        knee_raise_state_name = get_state_name(KneeRaiseState, EXERCISE_COUNTER.knee_raise_state)

        # Rep count
        new_rep = {
            'squat': EXERCISE_COUNTER.squat_counter,
            'bicep-curl': EXERCISE_COUNTER.curl_counter,
            'shoulder-flexion': EXERCISE_COUNTER.shoulder_flexion_counter,
            'knee-raise': EXERCISE_COUNTER.knee_raise_counter
        }.get(request.current_exercise, 0)

        # --- FEEDBACK LOGIC ---
        correction_feedback = ""
        
        # 1. Check for Rep Completion (Highest Priority)
        if feedback_manager and new_rep > old_rep:
            post_rep_feedbacks = feedback_manager.get_feedback()
            if post_rep_feedbacks:
                correction_feedback = post_rep_feedbacks[0] # Take top feedback
            else:
                correction_feedback = "TỐT LẮM!"
            feedback_manager.clear_feedback()
            prev_reps[request.current_exercise] = new_rep
        
        # 2. Check for Real-time Corrections (Medium Priority)
        elif feedback_manager:
            realtime_feedbacks = feedback_manager.get_feedback()
            if realtime_feedbacks:
                 correction_feedback = realtime_feedbacks[0] # Take top feedback

        # 3. State Guidance (Lowest Priority - Default)
        state_guidance_map = {
            'squat': {
                'IDLE': "Đứng thẳng",
                'SQUAT_START': "Hạ thấp người xuống",
                'SQUAT_DOWN': "Đứng lên!",
                'SQUAT_HOLD': "Giữ lại"
            },
            'bicep-curl': {
                'IDLE': "Duỗi thẳng tay",
                'CURL_START': "Gập tay lên",
                'CURL_UP': "Hạ tay xuống",
                'CURL_HOLD': "Giữ lại"
            },
            'shoulder-flexion': {
                'IDLE': "Hạ tay xuống",
                'FLEXION_START': "Nâng tay lên cao",
                'FLEXION_UP': "Hạ tay xuống",
                'FLEXION_DOWN': "Tiếp tục hạ"
            },
            'knee-raise': {
                'IDLE': "Đứng thẳng",
                'RAISE_START': "Nâng cao đùi & tay",
                'RAISE_UP': "Hạ xuống",
                'RAISE_DOWN': "Tiếp tục"
            }
        }
        
        current_state_name = {
            'squat': squat_state_name,
            'bicep-curl': curl_state_name,
            'shoulder-flexion': shoulder_flexion_state_name,
            'knee-raise': knee_raise_state_name
        }.get(request.current_exercise, 'IDLE')
        
        guidance_text = state_guidance_map.get(request.current_exercise, {}).get(current_state_name, "")
        
        # Combine using Stabilizer
        final_feedback = FEEDBACK_STATE.get_display_feedback(correction_feedback, guidance_text)

        # Session duration
        exercise_key = request.current_exercise.replace('-', '_')
        start_time = getattr(EXERCISE_COUNTER, f"{exercise_key}_start_time", None)
        session_duration = time.time() - start_time if start_time else 0

        # === GHI LOG - CHỈ KHI CÓ TĂNG SỐ LẦN TẬP ===
        # Only log when there's an actual rep increase to prevent false session recording
        if feedback_manager and new_rep > old_rep:
            now = datetime.now()
            log_data = {
                'user_id': request.user_id,
                'date': now.strftime("%d/%m/%Y"),
                'exercise_type': request.current_exercise,
                'feedback': final_feedback,
                'rep_count': new_rep,
                'session_duration': session_duration,
            }
            log_to_postgres(log_data)
        elif new_rep == 0 and session_duration > 5:
            # If no reps after 5 seconds, show warning
            # Don't override sticky feedback with this warning unless critical
            pass 


        # === TRẢ KẾT QUẢ ===
        return ProcessResponse(
            squat_count=EXERCISE_COUNTER.squat_counter,
            curl_count=EXERCISE_COUNTER.curl_counter,
            shoulder_flexion_count=EXERCISE_COUNTER.shoulder_flexion_counter,
            knee_raise_count=EXERCISE_COUNTER.knee_raise_counter,
            total_reps=EXERCISE_COUNTER.total_reps,
            squat_state_name=squat_state_name,
            curl_state_name=curl_state_name,
            shoulder_flexion_state_name=shoulder_flexion_state_name,
            knee_raise_state_name=knee_raise_state_name,
            feedback=final_feedback
        )
    
    except Exception as e:
        # DETAILED ERROR LOGGING
        print(f"\n{'='*60}")
        print(f"[ERROR] process_landmarks failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error msg: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        # Return fallback response to prevent frontend crash
        return ProcessResponse(
            squat_count=EXERCISE_COUNTER.squat_counter,
            curl_count=EXERCISE_COUNTER.curl_counter,
            shoulder_flexion_count=EXERCISE_COUNTER.shoulder_flexion_counter,
            knee_raise_count=EXERCISE_COUNTER.knee_raise_counter,
            total_reps=EXERCISE_COUNTER.total_reps,
            squat_state_name="ERROR",
            curl_state_name="ERROR",
            shoulder_flexion_state_name="ERROR",
            knee_raise_state_name="ERROR",
            feedback="Lỗi xử lý"
        )
        print(f"Error message: {str(e)}")
        if hasattr(request, 'landmarks') and request.landmarks:
            print(f"Number of landmarks: {len(request.landmarks)}")
            # Log first landmark for debugging
            if len(request.landmarks) > 0:
                lm = request.landmarks[0]
                print(f"Sample landmark[0]: x={lm.x}, y={lm.y}, z={lm.z}, vis={lm.visibility}")
        print(f"Exercise: {request.current_exercise if hasattr(request, 'current_exercise') else 'N/A'}")
        print(f"{'='*60}\n")
        raise


# --- Dashboard APIs ---
@app.get("/api/overall-stats")
async def get_overall_stats(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(
            func.count(func.distinct(ExerciseLogSimple.date)),
            func.sum(ExerciseLogSimple.rep_count),
            func.sum(ExerciseLogSimple.session_duration)
        )
        if user_id:
            query = query.filter(ExerciseLogSimple.user_id == user_id)
        
        row = query.first()
        return {
            "total_days": row[0] or 0,
            "total_reps": row[1] or 0,
            "total_duration": float(row[2] or 0)
        }
    except Exception as e:
        print(f"Error in overall-stats: {e}")
        return {"total_days": 0, "total_reps": 0, "total_duration": 0}

@app.get("/api/weekly-progress")
async def get_weekly_progress(user_id: Optional[str] = None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        where_clause = "WHERE user_id = %s" if user_id else ""
        params = (user_id,) if user_id else ()
        
        # Get max reps per exercise per day (simplified history)
        cur.execute(f"""
            SELECT date, exercise_type, MAX(rep_count) 
            FROM exercise_logs_simple 
            {where_clause}
            GROUP BY date, exercise_type 
            ORDER BY date DESC LIMIT 10
        """, params)
        rows = cur.fetchall()
        return [{"date": r[0], "exercise_type": r[1], "max_reps": r[2]} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/doctor-id")
async def get_doctor_id():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM users WHERE role = 'doctor' LIMIT 1")
        row = cur.fetchone()
        if row:
            return {"doctor_id": row[0]}
        raise HTTPException(status_code=404, detail="No doctor found")
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/recent-activity")
async def get_recent_activity():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Get latest 20 activities across all users
        cur.execute("""
            SELECT 
                el.id,
                el.user_id,
                u.full_name,
                u.username,
                el.exercise_type,
                el.rep_count,
                el.session_duration,
                el.created_at,
                el.feedback
            FROM exercise_logs_simple el
            JOIN users u ON el.user_id = u.user_id
            ORDER BY el.created_at DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/doctors")
async def get_doctors():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT user_id, full_name, username, email 
            FROM users 
            WHERE role = 'doctor'
            ORDER BY full_name
        """)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/patients")
async def get_patients():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT user_id as patient_id, full_name, username, email, role, created_at 
            FROM users 
            WHERE role = 'patient'
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        return_db_connection(conn)

class PatientCreate(BaseModel):
    full_name: str
    email: str
    username: str
    password: str

@app.post("/api/patients")
async def create_patient(req: PatientCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if username exists
        cur.execute("SELECT 1 FROM users WHERE username = %s", (req.username,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        cur.execute("""
            INSERT INTO users (username, password_hash, full_name, email, role)
            VALUES (%s, %s, %s, %s, 'patient')
            RETURNING user_id
        """, (req.username, req.password, req.full_name, req.email))
        user_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "created", "user_id": user_id}
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Delete related data first (optional, or rely on cascade if configured, but safe to do manually)
        cur.execute("DELETE FROM exercise_logs_simple WHERE user_id = %s", (patient_id,))
        cur.execute("DELETE FROM schedules WHERE patient_id = %s", (patient_id,))
        cur.execute("DELETE FROM assignments WHERE patient_id = %s", (patient_id,))
        cur.execute("DELETE FROM messages WHERE sender_id = %s OR receiver_id = %s", (patient_id, patient_id))
        
        cur.execute("DELETE FROM users WHERE user_id = %s", (patient_id,))
        conn.commit()
        return {"status": "deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

# === AUTHENTICATION MODELS ===
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str  # UUID
    username: str
    full_name: str
    role: str

# === AUTH API ===
@app.post("/api/login", response_model=UserResponse)
async def login(req: LoginRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Simple plain text password check for demo (Use bcrypt in production!)
        cur.execute("SELECT user_id, username, full_name, role FROM users WHERE username = %s AND password_hash = %s", (req.username, req.password))
        user = cur.fetchone()
        if user:
            return UserResponse(user_id=user[0], username=user[1], full_name=user[2], role=user[3])
        else:
            raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    finally:
        cur.close()
        return_db_connection(conn)

# === MESSAGING API ===
class MessageRequest(BaseModel):
    sender_id: str  # UUID
    receiver_id: str  # UUID
    content: str

@app.get("/api/conversations/{user_id}")
async def get_conversations(user_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Get list of users who have exchanged messages with this user
        # This is a bit complex SQL to get the latest message for each conversation
        cur.execute("""
            WITH LastMessages AS (
                SELECT 
                    CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END as other_user_id,
                    MAX(created_at) as last_msg_time
                FROM messages
                WHERE sender_id = %s OR receiver_id = %s
                GROUP BY other_user_id
            )
            SELECT u.user_id, u.full_name, u.role, lm.last_msg_time
            FROM LastMessages lm
            JOIN users u ON lm.other_user_id = u.user_id
            ORDER BY lm.last_msg_time DESC
        """, (user_id, user_id, user_id))
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/messages/{user_id}")
async def get_messages(user_id: str, other_user_id: str = None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if other_user_id:
            cur.execute("""
                SELECT m.content, m.created_at, m.sender_id, u.full_name 
                FROM messages m
                JOIN users u ON m.sender_id = u.user_id
                WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
                ORDER BY created_at ASC
            """, (user_id, other_user_id, other_user_id, user_id))
            rows = cur.fetchall()
            return [{"content": r[0], "created_at": r[1], "sender_id": r[2], "sender_name": r[3]} for r in rows]
        else:
             # Fallback if no specific user selected (maybe return empty or all recent?)
             return []
    finally:
        cur.close()
        return_db_connection(conn)

@app.post("/api/messages")
async def send_message(req: MessageRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)", 
                   (req.sender_id, req.receiver_id, req.content))
        conn.commit()
        return {"status": "sent"}
    finally:
        cur.close()
        return_db_connection(conn)

# === COMBO & PLAN API ===

class ComboItem(BaseModel):
    exercise_type: str
    sequence_order: int
    target_reps: int = 10
    duration_seconds: int = 0
    instructions: str = ""

class ComboCreate(BaseModel):
    doctor_id: str
    name: str
    description: str = ""
    items: List[ComboItem]

@app.post("/api/combos")
async def create_combo(req: ComboCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Create Combo
        cur.execute("""
            INSERT INTO combos (doctor_id, name, description)
            VALUES (%s, %s, %s)
            RETURNING combo_id
        """, (req.doctor_id, req.name, req.description))
        combo_id = cur.fetchone()[0]

        # Create Items
        if req.items:
            items_data = [
                (combo_id, item.exercise_type, item.sequence_order, item.target_reps, item.duration_seconds, item.instructions)
                for item in req.items
            ]
            execute_values(cur, """
                INSERT INTO combo_items (combo_id, exercise_type, sequence_order, target_reps, duration_seconds, instructions)
                VALUES %s
            """, items_data)
        
        conn.commit()
        return {"status": "created", "combo_id": combo_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/combos")
async def get_combos(doctor_id: Optional[str] = None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        where = "WHERE doctor_id = %s" if doctor_id else ""
        params = (doctor_id,) if doctor_id else ()
        
        cur.execute(f"SELECT * FROM combos {where} ORDER BY created_at DESC", params)
        combos = cur.fetchall()
        
        # Fetch items for each combo (could be optimized with join, but simple loop is fine for now)
        for combo in combos:
            cur.execute("""
                SELECT * FROM combo_items 
                WHERE combo_id = %s 
                ORDER BY sequence_order ASC
            """, (combo['combo_id'],))
            combo['items'] = cur.fetchall()
            
        return combos
    finally:
        cur.close()
        return_db_connection(conn)

class AssignPlanRequest(BaseModel):
    patient_id: str
    doctor_id: str
    exercise_type: Optional[str] = None
    combo_id: Optional[int] = None
    target_reps: int = 10
    assigned_date: str # YYYY-MM-DD
    session_time: Optional[str] = None # Morning, Afternoon, Evening

@app.post("/api/assign_plan")
async def assign_plan(req: AssignPlanRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if not req.exercise_type and not req.combo_id:
            raise HTTPException(status_code=400, detail="Either exercise_type or combo_id must be provided")

        if req.exercise_type and req.combo_id:
            raise HTTPException(status_code=400, detail="Cannot assign both a single exercise and a combo")

        if req.exercise_type:
            # Insert single exercise
            cur.execute("""
                INSERT INTO assignments (patient_id, doctor_id, exercise_type, target_reps, assigned_date, session_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (req.patient_id, req.doctor_id, req.exercise_type, req.target_reps, req.assigned_date, req.session_time))
        
        elif req.combo_id:
            # Get combo items
            cur.execute("SELECT exercise_type, target_reps FROM combo_items WHERE combo_id = %s ORDER BY sequence_order", (req.combo_id,))
            items = cur.fetchall()
            
            if not items:
                raise HTTPException(status_code=404, detail="Combo empty or not found")
                
            # Assign each item in the combo
            for item in items:
                cur.execute("""
                    INSERT INTO assignments (patient_id, doctor_id, exercise_type, target_reps, assigned_date, session_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (req.patient_id, req.doctor_id, item['exercise_type'], item['target_reps'], req.assigned_date, req.session_time))
        
        conn.commit()
        return {"status": "assigned"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/patient/today/{patient_id}")
async def get_patient_today_plan(patient_id: str):
    if not patient_id or patient_id == "null" or patient_id == "undefined":
        return []
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get assignments for today
        cur.execute("""
            SELECT a.*, c.name as combo_name, c.description as combo_desc, a.session_time
            FROM assignments a
            LEFT JOIN combos c ON a.combo_id = c.combo_id
            WHERE a.patient_id = %s AND a.assigned_date = %s AND a.status = 'active'
        """, (patient_id, today))
        assignments = cur.fetchall()
        
        plan_items = []
        for assign in assignments:
            if assign['combo_id']:
                # Expand combo
                cur.execute("""
                    SELECT * FROM combo_items WHERE combo_id = %s ORDER BY sequence_order ASC
                """, (assign['combo_id'],))
                items = cur.fetchall()
                for item in items:
                    plan_items.append({
                        "type": "exercise" if item['exercise_type'] != 'brain_game' else 'brain_game',
                        "name": item['exercise_type'],
                        "target": item['target_reps'],
                        "duration": item['duration_seconds'],
                        "instructions": item['instructions'],
                        "assignment_id": assign['assignment_id']
                    })
            else:
                # Single exercise
                plan_items.append({
                    "type": "exercise",
                    "name": assign['exercise_type'],
                    "target": assign['target_reps'],
                    "duration": 0,
                    "instructions": "Bài tập đơn lẻ",
                    "assignment_id": assign['assignment_id']
                })
        
        return plan_items
    finally:
        cur.close()
        return_db_connection(conn)

# === SESSION & DASHBOARD API ===

class SessionStart(BaseModel):
    user_id: str

@app.post("/api/session/start")
async def start_session(req: SessionStart):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO workout_sessions (user_id, start_time, status)
            VALUES (%s, NOW(), 'in_progress')
            RETURNING session_id
        """, (req.user_id,))
        session_id = cur.fetchone()[0]
        conn.commit()
        return {"session_id": session_id}
    finally:
        cur.close()
        return_db_connection(conn)

class SessionLog(BaseModel):
    session_id: str
    exercise_type: str
    reps_completed: int
    duration_seconds: int
    mistakes_count: int = 0
    accuracy_score: float = 0.0

@app.post("/api/session/log")
async def log_session_detail(req: SessionLog):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO session_details (session_id, exercise_type, reps_completed, duration_seconds, mistakes_count, accuracy_score)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (req.session_id, req.exercise_type, req.reps_completed, req.duration_seconds, req.mistakes_count, req.accuracy_score))
        
        # Update session last active time (optional, or just rely on end_time later)
        conn.commit()
        return {"status": "logged"}
    finally:
        cur.close()
        return_db_connection(conn)

@app.post("/api/session/end/{session_id}")
async def end_session(session_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE workout_sessions 
            SET end_time = NOW(), status = 'completed'
            WHERE session_id = %s
        """, (session_id,))
        conn.commit()
        return {"status": "ended"}
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/doctor/dashboard")
async def get_doctor_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 1. Active Patients (Sessions in progress within last 1 hour)
        cur.execute("""
            SELECT s.session_id, s.start_time, u.full_name, u.user_id
            FROM workout_sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.status = 'in_progress' 
            AND s.start_time > NOW() - INTERVAL '1 hour'
            ORDER BY s.start_time DESC
        """)
        active_patients = cur.fetchall()
        
        # 2. Recent Completed Sessions
        cur.execute("""
            SELECT s.session_id, s.end_time, u.full_name, 
                   (SELECT COUNT(*) FROM session_details d WHERE d.session_id = s.session_id) as exercise_count,
                   (SELECT SUM(duration_seconds) FROM session_details d WHERE d.session_id = s.session_id) as total_duration
            FROM workout_sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.status = 'completed'
            ORDER BY s.end_time DESC
            LIMIT 10
        """)
        recent_sessions = cur.fetchall()
        
        return {
            "active_patients": active_patients,
            "recent_sessions": recent_sessions
        }
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT * FROM session_details WHERE session_id = %s ORDER BY completed_at ASC
        """, (session_id,))
        details = cur.fetchall()
        return details
    finally:
        cur.close()
        return_db_connection(conn)


# === SCHEDULING API ===
class ScheduleRequest(BaseModel):
    patient_id: str
    doctor_id: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

@app.get("/api/schedules/{user_id}")
async def get_schedules(user_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if user is doctor or patient
        cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
        role_row = cur.fetchone()
        role = role_row[0] if role_row else 'patient'

        if role == 'doctor':
             cur.execute("""
                SELECT s.schedule_id, s.start_time, s.end_time, s.notes, u.full_name as patient_name, s.patient_id
                FROM schedules s
                LEFT JOIN users u ON s.patient_id = u.user_id
                WHERE s.doctor_id = %s
                ORDER BY s.start_time ASC
            """, (user_id,))
             rows = cur.fetchall()
             return [{"id": r[0], "start": r[1], "end": r[2], "notes": r[3], "title": r[4], "patient_id": r[5]} for r in rows]
        else:
            cur.execute("""
                SELECT s.schedule_id, s.start_time, s.end_time, s.notes, u.full_name as doctor_name
                FROM schedules s
                LEFT JOIN users u ON s.doctor_id = u.user_id
                WHERE s.patient_id = %s
                ORDER BY s.start_time ASC
            """, (user_id,))
            rows = cur.fetchall()
            return [{"id": r[0], "start": r[1], "end": r[2], "notes": r[3], "doctor": r[4]} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

@app.post("/api/schedules")
async def create_schedule(req: ScheduleRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO schedules (patient_id, doctor_id, start_time, end_time, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING schedule_id
        """, (req.patient_id, req.doctor_id, req.start_time, req.end_time, req.notes))
        schedule_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "created", "schedule_id": schedule_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM schedules WHERE schedule_id = %s", (schedule_id,))
        conn.commit()
        return {"status": "deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

# === ASSIGNMENT API ===
class AssignmentRequest(BaseModel):
    patient_id: str
    doctor_id: str
    exercise_type: str
    target_reps: int
    frequency: str
    difficulty: Optional[str] = 'Medium'
    duration_mins: Optional[int] = 15
    sets: Optional[int] = 3

@app.get("/api/assignments/{patient_id}")
async def get_assignments(patient_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Check if columns exist, if not, we might need to migrate or just select what exists
        # For now assuming simple schema, but let's add columns if needed in ensure_table_exists
        cur.execute("""
            SELECT assignment_id as id, exercise_type as name, target_reps, frequency as freq, 
                   status, assigned_date
            FROM assignments 
            WHERE patient_id = %s
        """, (patient_id,))
        rows = cur.fetchall()
        
        # Map to frontend format
        results = []
        for r in rows:
            results.append({
                "id": r['id'],
                "name": r['name'],
                "icon": "🏋️", # Placeholder
                "duration": 15, # Default
                "sets": 3, # Default
                "freq": r['freq'],
                "difficulty": "Medium", # Default
                "target_reps": r['target_reps']
            })
        return results
    finally:
        cur.close()
        return_db_connection(conn)

@app.post("/api/assignments")
async def create_assignment(req: AssignmentRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO assignments (patient_id, doctor_id, exercise_type, target_reps, frequency)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING assignment_id
        """, (req.patient_id, req.doctor_id, req.exercise_type, req.target_reps, req.frequency))
        assignment_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "created", "assignment_id": assignment_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.delete("/api/assignments/{assignment_id}")
async def delete_assignment(assignment_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM assignments WHERE assignment_id = %s", (assignment_id,))
        conn.commit()
        return {"status": "deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

# === BRAIN EXERCISE API ===
class BrainExerciseSubmit(BaseModel):
    user_id: str
    exercise_type: str
    is_correct: bool
    question_number: int

class BrainExerciseComplete(BaseModel):
    user_id: str
    exercise_type: str
    score: int
    total_questions: int

@app.post("/api/brain-exercise/submit")
async def submit_brain_exercise(req: BrainExerciseSubmit):
    """Log a single brain exercise attempt"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Create table if not exists
        # Table creation moved to ensure_table_exists

        
        cur.execute("""
            INSERT INTO brain_exercise_logs (user_id, exercise_type, is_correct, question_number)
            VALUES (%s, %s, %s, %s)
        """, (req.user_id, req.exercise_type, req.is_correct, req.question_number))
        conn.commit()
        return {"status": "logged"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.post("/api/brain-exercise/complete")
async def complete_brain_exercise(req: BrainExerciseComplete):
    """Log completion of a brain exercise game"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Create table if not exists
        # Table creation moved to ensure_table_exists

        
        percentage = (req.score / req.total_questions * 100) if req.total_questions > 0 else 0
        
        cur.execute("""
            INSERT INTO brain_exercise_sessions (user_id, exercise_type, score, total_questions, percentage)
            VALUES (%s, %s, %s, %s, %s)
        """, (req.user_id, req.exercise_type, req.score, req.total_questions, percentage))
        conn.commit()
        return {"status": "completed", "percentage": percentage}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/brain-exercise/stats/{user_id}")
async def get_brain_exercise_stats(user_id: str):
    """Get user's brain exercise statistics"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get today's score
        cur.execute("""
            SELECT COALESCE(SUM(score), 0) as today_score
            FROM brain_exercise_sessions
            WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE
        """, (user_id,))
        today_row = cur.fetchone()
        today_score = today_row[0] if today_row else 0
        
        # Get streak (consecutive days)
        cur.execute("""
            SELECT COUNT(DISTINCT DATE(created_at)) as streak
            FROM brain_exercise_sessions
            WHERE user_id = %s 
            AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        """, (user_id,))
        streak_row = cur.fetchone()
        streak = streak_row[0] if streak_row else 0
        
        # Get total games played
        cur.execute("""
            SELECT COUNT(*) as total_games,
                   COALESCE(AVG(percentage), 0) as avg_percentage
            FROM brain_exercise_sessions
            WHERE user_id = %s
        """, (user_id,))
        stats_row = cur.fetchone()
        total_games = stats_row[0] if stats_row else 0
        avg_percentage = float(stats_row[1]) if stats_row and stats_row[1] else 0
        
        return {
            "today_score": int(today_score),
            "streak": int(streak),
            "total_games": int(total_games),
            "avg_percentage": round(avg_percentage, 1)
        }
    except Exception as e:
        print(f"Error getting brain exercise stats: {e}")
        return {"today_score": 0, "streak": 0, "total_games": 0, "avg_percentage": 0}
    finally:
        cur.close()
        return_db_connection(conn)

# === DOCTOR DASHBOARD APIs ===
@app.get("/api/patient-sessions/{patient_id}")
async def get_patient_sessions(patient_id: str):
    """Get all exercise sessions for a specific patient"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get sessions from exercise_logs_simple
        cur.execute("""
            SELECT 
                id as session_id,
                date as start_time,
                exercise_type,
                rep_count as total_reps_completed,
                session_duration as session_duration_seconds,
                0 as total_errors_detected,
                feedback,
                created_at
            FROM exercise_logs_simple
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (patient_id,))
        rows = cur.fetchall()
        
        sessions = []
        for r in rows:
            sessions.append({
                "session_id": r[0],
                "start_time": r[1].isoformat() if r[1] else None,
                "exercise_type": r[2],
                "total_reps_completed": r[3] or 0,
                "session_duration_seconds": int(r[4] or 0),
                "total_errors_detected": r[5] or 0,
                "feedback": r[6],
                "created_at": r[7].isoformat() if r[7] else None
            })
        
        return sessions
    except Exception as e:
        print(f"Error fetching patient sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/patient-logs/{patient_id}")
async def get_patient_logs(patient_id: str):
    """Get detailed logs for a patient (for form score calculation)"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Calculate form scores based on rep count and session duration
        cur.execute("""
            SELECT 
                id,
                date,
                exercise_type,
                rep_count,
                session_duration,
                CASE 
                    WHEN rep_count >= 10 THEN 85 + (rep_count - 10) * 2
                    WHEN rep_count >= 5 THEN 70 + (rep_count - 5) * 3
                    ELSE 50 + rep_count * 4
                END as form_score
            FROM exercise_logs_simple
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 100
        """, (patient_id,))
        rows = cur.fetchall()
        
        logs = []
        for r in rows:
            logs.append({
                "log_id": r[0],
                "timestamp": r[1].isoformat() if r[1] else None,
                "exercise_type": r[2],
                "rep_count": r[3] or 0,
                "session_duration": float(r[4] or 0),
                "form_score": min(100, r[5] or 0)  # Cap at 100
            })
        
        return logs
    except Exception as e:
        print(f"Error fetching patient logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        return_db_connection(conn)

@app.get("/api/patients/{patient_id}")
async def get_patient_detail(patient_id: str):
    """Get detailed information for a specific patient"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT user_id, username, email, full_name, role, created_at
            FROM users
            WHERE user_id = %s AND role = 'patient'
        """, (patient_id,))
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {
            "patient_id": row[0],
            "username": row[1],
            "email": row[2],
            "full_name": row[3],
            "role": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        }
    finally:
        cur.close()
        return_db_connection(conn)

# === KHỞI ĐỘNG HOÀN TẤT ===
print("ỨNG DỤNG SẴN SÀNG! Truy cập: http://127.0.0.1:8000/docs")