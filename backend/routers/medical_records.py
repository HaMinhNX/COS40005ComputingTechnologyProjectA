from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from models import User, MedicalRecord
from dependencies import get_current_user, verify_patient_access
from schemas import MedicalRecordUpdate

router = APIRouter(
    prefix="/api/medical-records",
    tags=["medical-records"]
)

@router.get("/{patient_id}")
async def get_medical_record(patient_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get medical record for a patient"""
    # Authorization check
    verify_patient_access(patient_id, current_user, db)
    
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    if not record:
        # Create empty record if not exists
        record = MedicalRecord(patient_id=patient_id)
        db.add(record)
        db.commit()
        db.refresh(record)
    
    return record

@router.put("/{patient_id}")
async def update_medical_record(patient_id: UUID, data: MedicalRecordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update medical record for a patient"""
    # Authorization check
    verify_patient_access(patient_id, current_user, db)
    
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    if not record:
        record = MedicalRecord(patient_id=patient_id)
        db.add(record)
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)
    
    try:
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
