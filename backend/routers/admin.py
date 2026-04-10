from datetime import datetime, timezone
import os
import smtplib
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, aliased

from database import get_db
from dependencies import get_current_admin
from enums import DoctorApprovalStatus, UserRole
from models import DoctorVerification, User


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)


def send_doctor_review_email(recipient: str, approved: bool, full_name: str, rejection_reason: str | None = None):
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    website_url = os.getenv("FRONTEND_URL", "https://haming.vercel.app")

    if approved:
        subject = "Doctor registration approved"
        body = (
            f"Hello {full_name},\n\n"
            "Your doctor registration has been approved.\n"
            f"You can now log in here: {website_url}\n\n"
            "Best regards,\nHaminG Team"
        )
    else:
        subject = "Doctor registration declined"
        body = (
            f"Hello {full_name},\n\n"
            "Your doctor registration has been declined.\n"
            f"Reason: {rejection_reason or 'Not specified'}\n\n"
            "Please review your documents and submit a new request.\n\n"
            "Best regards,\nHaminG Team"
        )

    if not sender or not password:
        print(f"SMTP config missing. Fake sent doctor review email to {recipient}: {subject}")
        return

    msg = MIMEMultipart()
    msg["From"] = f"HaminG <{sender}>"
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send doctor review email: {e}")


class RejectDoctorPayload(BaseModel):
    rejection_reason: str | None = None


def _build_registration_item(user: User, verification: DoctorVerification, reviewer: User | None = None):
    return {
        "doctor_id": str(user.user_id),
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "approval_status": user.approval_status,
        "submitted_at": verification.submitted_at,
        "reviewed_at": verification.reviewed_at,
        "reviewed_by_name": reviewer.full_name if reviewer else None,
        "rejection_reason": verification.rejection_reason,
        "certificate_url": verification.certificate_url,
    }


@router.get("/doctor-registrations/pending")
async def list_pending_doctor_registrations(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    pending_doctors = (
        db.query(User, DoctorVerification)
        .join(DoctorVerification, DoctorVerification.doctor_id == User.user_id)
        .filter(
            User.role == UserRole.DOCTOR.value,
            User.approval_status == DoctorApprovalStatus.PENDING.value
        )
        .order_by(DoctorVerification.submitted_at.asc())
        .all()
    )

    return [
        _build_registration_item(user, verification)
        for user, verification in pending_doctors
    ]


@router.get("/doctor-registrations/history")
async def list_doctor_registration_history(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    doctor_user = aliased(User)
    reviewer_user = aliased(User)
    reviewed_rows = (
        db.query(doctor_user, DoctorVerification, reviewer_user)
        .join(DoctorVerification, DoctorVerification.doctor_id == doctor_user.user_id)
        .outerjoin(reviewer_user, DoctorVerification.reviewed_by == reviewer_user.user_id)
        .filter(
            doctor_user.role == UserRole.DOCTOR.value,
            doctor_user.approval_status.in_([
                DoctorApprovalStatus.APPROVED.value,
                DoctorApprovalStatus.REJECTED.value,
            ])
        )
        .order_by(DoctorVerification.reviewed_at.desc().nullslast(), DoctorVerification.submitted_at.desc())
        .all()
    )

    return [
        _build_registration_item(doctor_user, verification, reviewer_user)
        for doctor_user, verification, reviewer_user in reviewed_rows
    ]


@router.get("/doctor-registrations/{doctor_id}/document")
async def download_doctor_registration_document(
    doctor_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    verification = db.query(DoctorVerification).filter(DoctorVerification.doctor_id == doctor_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Doctor verification request not found")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(verification.certificate_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to download certificate: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch certificate from storage")

    content_type = response.headers.get("content-type", "application/octet-stream")
    public_id = verification.certificate_public_id or f"doctor_certificate_{doctor_id}"
    filename = public_id.split("/")[-1]
    if "." not in filename:
        if "pdf" in content_type:
            filename += ".pdf"
        elif "png" in content_type:
            filename += ".png"
        elif "jpeg" in content_type or "jpg" in content_type:
            filename += ".jpg"
        else:
            filename += ".bin"

    headers = {"Content-Disposition": f"attachment; filename=\"{filename}\""}
    return StreamingResponse(BytesIO(response.content), media_type=content_type, headers=headers)


@router.post("/doctor-registrations/{doctor_id}/approve")
async def approve_doctor_registration(
    doctor_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    doctor = db.query(User).filter(User.user_id == doctor_id, User.role == UserRole.DOCTOR.value).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    verification = db.query(DoctorVerification).filter(DoctorVerification.doctor_id == doctor.user_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Doctor verification request not found")

    doctor.approval_status = DoctorApprovalStatus.APPROVED.value
    verification.reviewed_by = admin_user.user_id
    verification.reviewed_at = datetime.now(timezone.utc)
    verification.rejection_reason = None

    db.commit()
    send_doctor_review_email(doctor.email, approved=True, full_name=doctor.full_name or doctor.username)

    return {"message": "Doctor approved successfully"}


@router.post("/doctor-registrations/{doctor_id}/reject")
async def reject_doctor_registration(
    doctor_id: str,
    payload: RejectDoctorPayload,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    doctor = db.query(User).filter(User.user_id == doctor_id, User.role == UserRole.DOCTOR.value).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    verification = db.query(DoctorVerification).filter(DoctorVerification.doctor_id == doctor.user_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Doctor verification request not found")

    doctor.approval_status = DoctorApprovalStatus.REJECTED.value
    verification.reviewed_by = admin_user.user_id
    verification.reviewed_at = datetime.now(timezone.utc)
    verification.rejection_reason = payload.rejection_reason

    db.commit()
    send_doctor_review_email(
        doctor.email,
        approved=False,
        full_name=doctor.full_name or doctor.username,
        rejection_reason=payload.rejection_reason
    )

    return {"message": "Doctor rejected successfully"}
