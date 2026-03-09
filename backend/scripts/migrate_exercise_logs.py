import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
from datetime import timedelta

# Add current directory to path to import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Base, User, ExerciseLogSimple, WorkoutSession, SessionDetail
from enums import SessionStatus

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_data():
    db = SessionLocal()
    try:
        # Fetch all simple logs
        logs = db.query(ExerciseLogSimple).all()
        print(f"Found {len(logs)} logs to migrate")
        
        for log in logs:
            # Check if already migrated (optional, but good for idempotency)
            # We can't easily check without a mapping, so we'll just create new ones
            
            # Create WorkoutSession
            start_time = log.created_at - timedelta(seconds=float(log.session_duration))
            session = WorkoutSession(
                session_id=uuid4(),
                user_id=log.user_id,
                start_time=start_time,
                end_time=log.created_at,
                status=SessionStatus.COMPLETED.value
            )
            db.add(session)
            db.flush() # Get session_id
            
            # Create SessionDetail
            detail = SessionDetail(
                session_id=session.session_id,
                exercise_type=log.exercise_type,
                reps_completed=log.rep_count,
                duration_seconds=int(log.session_duration),
                feedback=log.feedback,
                completed_at=log.created_at
            )
            db.add(detail)
            
        db.commit()
        print("Migration completed successfully")
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()
