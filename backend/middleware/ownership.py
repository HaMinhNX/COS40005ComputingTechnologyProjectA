from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from models import User, Assignment, Schedule, WorkoutSession, BrainExerciseSession, BrainExerciseLog
from enums import UserRole
from dependencies import get_current_user

class ResourceAccess:
    """
    Utility class for resource-level access control.
    Provides dependencies to verify ownership and relationships.
    """

    @staticmethod
    async def patient(
        patient_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Verify access to a patient's data."""
        if current_user.role == UserRole.PATIENT.value:
            if current_user.user_id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only access your own data"
                )
            return current_user
        
        if current_user.role == UserRole.DOCTOR.value:
            # NEW: Relaxed check for doctors.
            # All doctors can access any patient's data in this system.
            # This aligns with the discovery UI and the AI Chat feature.
            patient = db.query(User).filter(User.user_id == patient_id).first()
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")
            return patient
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized role")

    @staticmethod
    async def session(
        session_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> WorkoutSession:
        """Verify access to a specific workout session."""
        session = db.query(WorkoutSession).filter(WorkoutSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")
        
        await ResourceAccess.patient(session.user_id, current_user, db)
        return session

    @staticmethod
    async def brain_session(
        session_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> BrainExerciseSession:
        """Verify access to a specific brain exercise session."""
        session = db.query(BrainExerciseSession).filter(BrainExerciseSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Brain exercise session not found")
        
        await ResourceAccess.patient(session.user_id, current_user, db)
        return session

    @staticmethod
    async def brain_log(
        log_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> BrainExerciseLog:
        """Verify access to a specific brain exercise log."""
        log = db.query(BrainExerciseLog).filter(BrainExerciseLog.log_id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Brain exercise log not found")
        
        await ResourceAccess.patient(log.user_id, current_user, db)
        return log

    @staticmethod
    async def assignment(
        assignment_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Assignment:
        """Verify access to an assignment."""
        assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        await ResourceAccess.patient(assignment.patient_id, current_user, db)
        return assignment

    @staticmethod
    async def schedule(
        schedule_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Schedule:
        """Verify access to a specific schedule."""
        schedule = db.query(Schedule).filter(Schedule.schedule_id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        await ResourceAccess.patient(schedule.patient_id, current_user, db)
        return schedule
