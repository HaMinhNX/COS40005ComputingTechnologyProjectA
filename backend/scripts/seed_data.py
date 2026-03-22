"""
Seed Data Script for VinaWork Application
Creates meaningful test data for demonstrating dashboard features.
Run with: python seed_data.py
"""
import os
import sys
from datetime import datetime, timedelta, date
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, WorkoutSession, SessionDetail, Assignment, PatientNote
from auth import get_password_hash
from enums import PatientStatus, SessionStatus

def create_seed_data():
    db = SessionLocal()
    
    try:
        print("🌱 Starting seed data creation...")
        
        # Check if demo data already exists
        existing_patients = db.query(User).filter(User.role == 'patient').count()
        if existing_patients > 3:
            print(f"✅ Found {existing_patients} patients. Seed data may already exist.")
            print("   Adding workout sessions for existing patients...")
            add_workout_data(db)
            return
        
        # Create demo doctor if not exists
        doctor = db.query(User).filter(User.username == 'doctor_demo').first()
        if not doctor:
            doctor = User(
                username='doctor_demo',
                password_hash=get_password_hash('demo123'),
                email='doctor@vinawork.vn',
                full_name='BS. Nguyễn Văn An',
                role='doctor',
                status=PatientStatus.ACTIVE.value,
                last_active_at=datetime.now()
            )
            db.add(doctor)
            db.commit()
            print("✅ Created demo doctor: doctor_demo / demo123")
        
        # Create demo patients with varied activity levels
        patients_data = [
            {'name': 'Trần Thị Bình', 'status': 'active', 'days_ago': 0},
            {'name': 'Lê Văn Cường', 'status': 'active', 'days_ago': 1},
            {'name': 'Phạm Thị Dung', 'status': 'active', 'days_ago': 2},
            {'name': 'Nguyễn Văn Em', 'status': 'needs_attention', 'days_ago': 5},
            {'name': 'Hoàng Thị Phượng', 'status': 'needs_attention', 'days_ago': 6},
            {'name': 'Vũ Đình Giang', 'status': 'inactive', 'days_ago': 10},
            {'name': 'Đặng Thị Hương', 'status': 'inactive', 'days_ago': 15},
        ]
        
        exercise_types = ['Squat', 'Bicep Curl', 'Shoulder Flexion', 'Knee Raise']
        
        for i, pdata in enumerate(patients_data):
            username = f'patient_demo_{i+1}'
            patient = db.query(User).filter(User.username == username).first()
            
            if not patient:
                patient = User(
                    username=username,
                    password_hash=get_password_hash('demo123'),
                    email=f'patient{i+1}@vinawork.vn',
                    full_name=pdata['name'],
                    role='patient',
                    status=pdata['status'],
                    last_active_at=datetime.now() - timedelta(days=pdata['days_ago']),
                    created_at=datetime.now() - timedelta(days=random.randint(10, 60))
                )
                db.add(patient)
                db.commit()
                print(f"✅ Created patient: {username} ({pdata['name']})")
            
            # Create workout sessions
            num_sessions = random.randint(3, 8) if pdata['status'] == 'active' else random.randint(1, 3)
            
            for j in range(num_sessions):
                session_date = datetime.now() - timedelta(days=pdata['days_ago'] + j)
                
                session = WorkoutSession(
                    user_id=patient.user_id,
                    start_time=session_date,
                    end_time=session_date + timedelta(minutes=random.randint(15, 45)),
                    status=SessionStatus.COMPLETED.value
                )
                db.add(session)
                db.commit()
                
                # Add session details
                for ex_type in random.sample(exercise_types, random.randint(2, 4)):
                    detail = SessionDetail(
                        session_id=session.session_id,
                        exercise_type=ex_type,
                        reps_completed=random.randint(8, 20),
                        duration_seconds=random.randint(60, 300),
                        mistakes_count=random.randint(0, 5),
                        accuracy_score=random.uniform(70, 98),
                        completed_at=session_date + timedelta(minutes=random.randint(5, 30))
                    )
                    db.add(detail)
            
            # Create assignments
            for ex_type in random.sample(exercise_types, 2):
                assignment = Assignment(
                    patient_id=patient.user_id,
                    doctor_id=doctor.user_id,
                    exercise_type=ex_type,
                    target_reps=random.randint(10, 20),
                    frequency='Daily',
                    assigned_date=date.today() - timedelta(days=random.randint(0, 7)),
                    session_time='Morning',
                    is_completed=random.choice([True, False])
                )
                db.add(assignment)
            
            # Create patient notes
            note_titles = ['Tiến bộ tốt', 'Cần theo dõi', 'Ghi chú định kỳ', 'Đánh giá tuần']
            note = PatientNote(
                patient_id=patient.user_id,
                doctor_id=doctor.user_id,
                title=random.choice(note_titles),
                content=f'Bệnh nhân {pdata["name"]} thực hiện bài tập ổn định. Cần tiếp tục theo dõi trong tuần tới.'
            )
            db.add(note)
        
        db.commit()
        print("\n🎉 Seed data created successfully!")
        print("   Demo accounts:")
        print("   - Doctor: doctor_demo / demo123")
        print("   - Patients: patient_demo_1 to patient_demo_7 / demo123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating seed data: {e}")
        raise
    finally:
        db.close()


def add_workout_data(db: Session):
    """Add workout data to existing patients"""
    patients = db.query(User).filter(User.role == 'patient').all()
    doctor = db.query(User).filter(User.role == 'doctor').first()
    
    if not doctor:
        print("❌ No doctor found. Please create a doctor first.")
        return
    
    exercise_types = ['Squat', 'Bicep Curl', 'Shoulder Flexion', 'Knee Raise']
    
    for patient in patients:
        # Check if patient already has sessions
        existing_sessions = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == patient.user_id
        ).count()
        
        if existing_sessions > 0:
            print(f"   Patient {patient.full_name} already has {existing_sessions} sessions")
            continue
        
        # Add sessions for the past week
        for days_ago in range(7):
            if random.random() > 0.4:  # 60% chance of workout each day
                session_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(8, 18))
                
                session = WorkoutSession(
                    user_id=patient.user_id,
                    start_time=session_date,
                    end_time=session_date + timedelta(minutes=random.randint(15, 45)),
                    status=SessionStatus.COMPLETED.value
                )
                db.add(session)
                db.commit()
                
                for ex_type in random.sample(exercise_types, random.randint(2, 4)):
                    detail = SessionDetail(
                        session_id=session.session_id,
                        exercise_type=ex_type,
                        reps_completed=random.randint(8, 20),
                        duration_seconds=random.randint(60, 300),
                        mistakes_count=random.randint(0, 5),
                        accuracy_score=random.uniform(70, 98),
                        completed_at=session_date + timedelta(minutes=random.randint(5, 30))
                    )
                    db.add(detail)
        
        # Update last_active_at
        patient.last_active_at = datetime.now() - timedelta(days=random.randint(0, 5))
        patient.status = PatientStatus.ACTIVE.value if random.random() > 0.3 else PatientStatus.NEEDS_ATTENTION.value
        
        print(f"✅ Added workout data for {patient.full_name}")
    
    db.commit()
    print("\n🎉 Workout data added successfully!")


if __name__ == '__main__':
    create_seed_data()
