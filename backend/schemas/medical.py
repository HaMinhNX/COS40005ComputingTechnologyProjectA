"""
Pydantic schemas for Medical Records and Patient Notes.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============ Medical Record Schemas ============

class MedicalRecordCreate(BaseModel):
    """Schema for creating a medical record"""
    patient_id: UUID
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment_plan: Optional[str] = None
    height_cm: Optional[Decimal] = Field(None, ge=0, le=300)
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=500)
    blood_type: Optional[str] = Field(None, max_length=5)


class MedicalRecordUpdate(BaseModel):
    """Schema for updating a medical record"""
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment_plan: Optional[str] = None
    height_cm: Optional[Decimal] = Field(None, ge=0, le=300)
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=500)
    blood_type: Optional[str] = Field(None, max_length=5)


class MedicalRecordResponse(BaseModel):
    """Schema for medical record response"""
    record_id: int
    patient_id: UUID
    diagnosis: Optional[str]
    symptoms: Optional[str]
    treatment_plan: Optional[str]
    height_cm: Optional[Decimal]
    weight_kg: Optional[Decimal]
    blood_type: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Patient Note Schemas ============

class PatientNoteCreate(BaseModel):
    """Schema for creating a patient note"""
    patient_id: UUID
    title: Optional[str] = Field(None, max_length=200)
    content: str


class PatientNoteUpdate(BaseModel):
    """Schema for updating a patient note"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None


class PatientNoteResponse(BaseModel):
    """Schema for patient note response"""
    note_id: int
    patient_id: UUID
    doctor_id: UUID
    title: Optional[str]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
