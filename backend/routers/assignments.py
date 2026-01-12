from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import User, Assignment, Combo
from dependencies import get_current_user, get_current_doctor, verify_patient_access
from schemas import AssignmentCreate, AssignmentResponse

router = APIRouter(
    prefix="/api",
    tags=["assignments"]
)

@router.get("/assignments/{patient_id}", response_model=List[AssignmentResponse])
async def get_assignments(patient_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all assignments for a patient"""
    verify_patient_access(patient_id, current_user, db)
    
    assignments = db.query(Assignment).filter(
        Assignment.patient_id == patient_id,
        Assignment.status == 'active'
    ).all()
    
    return assignments

@router.post("/assignments")
@router.post("/assign_plan")
async def create_assignment(data: AssignmentCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Create new assignment for a patient (handles single exercise or combo)"""
    try:
        if data.combo_id:
            # Handle combo assignment
            combo = db.query(Combo).filter(Combo.combo_id == data.combo_id).first()
            if not combo:
                raise HTTPException(status_code=404, detail="Combo not found")
            
            assignments = []
            for item in combo.items:
                new_assignment = Assignment(
                    patient_id=data.patient_id,
                    doctor_id=current_doctor.user_id,
                    exercise_type=item.exercise_type,
                    target_reps=item.target_reps,
                    frequency=data.frequency,
                    session_time=data.session_time,
                    notes=item.instructions or data.notes,
                    combo_id=combo.combo_id
                )
                db.add(new_assignment)
                assignments.append(new_assignment)
            
            db.commit()
            return {"message": f"Assigned combo '{combo.name}' with {len(assignments)} exercises"}
        
        else:
            # Handle single exercise assignment
            new_assignment = Assignment(
                patient_id=data.patient_id,
                doctor_id=current_doctor.user_id,
                exercise_type=data.exercise_type,
                target_reps=data.target_reps,
                frequency=data.frequency,
                session_time=data.session_time,
                notes=data.notes
            )
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)
            return AssignmentResponse.model_validate(new_assignment)
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: int, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Delete an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id,
        Assignment.doctor_id == current_doctor.user_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or unauthorized")
    
    try:
        db.delete(assignment)
        db.commit()
        return {"message": "Assignment deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
