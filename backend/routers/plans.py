from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from database import get_db
from models import User, Combo, ComboItem, WeekPlan, Assignment
from dependencies import get_current_user, get_current_doctor
from schemas import ComboCreate, WeekPlanCreate, ComboResponse, WeekPlanResponse

router = APIRouter(
    prefix="/api",
    tags=["plans"]
)

@router.get("/combos", response_model=List[ComboResponse])
async def get_combos(doctor_id: UUID = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all exercise combos. If doctor_id is provided, filter by that doctor."""
    query = db.query(Combo).options(joinedload(Combo.items))
    
    if doctor_id:
        query = query.filter(Combo.doctor_id == doctor_id)
    elif current_user.role == 'doctor':
        query = query.filter(Combo.doctor_id == current_user.user_id)
        
    return query.all()

@router.post("/combos", response_model=ComboResponse)
async def create_combo(data: ComboCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Create a new exercise combo"""
    try:
        new_combo = Combo(
            doctor_id=current_doctor.user_id,
            name=data.name,
            description=data.description
        )
        db.add(new_combo)
        db.flush()
        
        for i, item in enumerate(data.items):
            new_item = ComboItem(
                combo_id=new_combo.combo_id,
                exercise_type=item.exercise_type,
                sequence_order=i,
                target_reps=item.target_reps,
                duration_seconds=item.duration_seconds,
                instructions=item.instructions
            )
            db.add(new_item)
            
        db.commit()
        db.refresh(new_combo)
        return new_combo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/week-plans", response_model=WeekPlanResponse)
async def create_week_plan(data: WeekPlanCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Create a new week plan for a patient"""
    try:
        new_plan = WeekPlan(
            doctor_id=current_doctor.user_id,
            patient_id=data.patient_id,
            plan_name=data.plan_name,
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date
        )
        db.add(new_plan)
        db.flush()
        
        # Add assignments for each day
        for day_plan in data.days:
            for ex in day_plan.exercises:
                new_assignment = Assignment(
                    patient_id=data.patient_id,
                    doctor_id=current_doctor.user_id,
                    week_plan_id=new_plan.plan_id,
                    day_of_week=day_plan.day,
                    exercise_type=ex.exercise_type,
                    target_reps=ex.target_reps,
                    sets=ex.sets,
                    session_time=ex.session_time,
                    notes=ex.notes
                )
                db.add(new_assignment)
                
        db.commit()
        db.refresh(new_plan)
        return new_plan
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/week-plans/{patient_id}", response_model=List[WeekPlanResponse])
async def get_week_plans(patient_id: UUID, db: Session = Depends(get_db)):
    """Get all week plans for a patient"""
    return db.query(WeekPlan).filter(WeekPlan.patient_id == patient_id).order_by(WeekPlan.start_date.desc()).all()

@router.get("/patient/today/{user_id}")
async def get_today_plan(user_id: UUID, db: Session = Depends(get_db)):
    """Get today's exercises for a patient - includes both week plan and direct assignments"""
    from datetime import date
    from sqlalchemy import or_
    
    today = date.today()
    day_of_week = today.weekday() + 1  # 1=Monday, 7=Sunday
    
    all_assignments = []
    
    # 1. Get assignments from active week plans for today's day of week
    plan = db.query(WeekPlan).filter(
        WeekPlan.patient_id == user_id,
        WeekPlan.start_date <= today,
        WeekPlan.end_date >= today,
        WeekPlan.status == 'active'
    ).first()
    
    if plan:
        week_assignments = db.query(Assignment).filter(
            Assignment.week_plan_id == plan.plan_id,
            Assignment.day_of_week == day_of_week
        ).all()
        all_assignments.extend(week_assignments)
    
    # 2. Get direct assignments (no week plan) with assigned_date = today
    direct_assignments = db.query(Assignment).filter(
        Assignment.patient_id == user_id,
        Assignment.week_plan_id == None,  # Direct assignment, not from week plan
        Assignment.assigned_date == today
    ).all()
    all_assignments.extend(direct_assignments)
    
    # 3. Also get daily assignments (frequency = 'Daily')
    daily_assignments = db.query(Assignment).filter(
        Assignment.patient_id == user_id,
        Assignment.frequency == 'Daily'
    ).all()
    
    # Add daily assignments that aren't already in the list
    existing_ids = {a.assignment_id for a in all_assignments}
    for a in daily_assignments:
        if a.assignment_id not in existing_ids:
            all_assignments.append(a)
    
    return [
        {
            "id": a.assignment_id,
            "name": a.exercise_type,
            "target": a.target_reps,
            "sets": a.sets,
            "session_time": a.session_time,
            "is_completed": a.is_completed,
            "instructions": a.notes,
            "type": "exercise"
        }
        for a in all_assignments
    ]
