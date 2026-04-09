from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from datetime import date
from database import get_db
from models import WearableHealthData
from dependencies import get_current_user
from models import User
from pydantic import BaseModel
from typing import Optional
import statistics

router = APIRouter(prefix="/api/wearable", tags=["wearable"])


class WearableUploadSchema(BaseModel):
    device: Optional[str] = None
    week: Optional[str] = None  # e.g. "2026-03-28 to 2026-04-03"
    weekly_summary: dict
    daily_records: list


def _get_latest_record_for_user(user_id: UUID, db: Session):
    return db.query(WearableHealthData).filter(
        WearableHealthData.user_id == user_id
    ).order_by(desc(WearableHealthData.week_start)).first()


@router.post("/upload")
async def upload_wearable_data(
    data: WearableUploadSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = data.weekly_summary

    # Parse week_start and week_end from the week string
    try:
        parts = data.week.split(" to ") if data.week else [None, None]
        week_start = date.fromisoformat(parts[0].strip()) if parts[0] else None
        week_end = date.fromisoformat(parts[1].strip()) if len(parts) > 1 and parts[1] else None
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid week format. Expected 'YYYY-MM-DD to YYYY-MM-DD'")

    # Fallback to date range from daily records when week is absent.
    if not week_start or not week_end:
        daily_dates = []
        for day in data.daily_records or []:
            day_date = day.get("date") if isinstance(day, dict) else None
            if day_date:
                try:
                    daily_dates.append(date.fromisoformat(day_date))
                except Exception:
                    continue
        if daily_dates:
            week_start = min(daily_dates)
            week_end = max(daily_dates)

    if not week_start or not week_end:
        raise HTTPException(status_code=400, detail="Missing valid date range. Provide 'week' or daily_records[].date")

    # Compute avg resting HR and avg sleep duration from daily records
    resting_hrs = []
    sleep_durations = []
    for d in data.daily_records or []:
        if not isinstance(d, dict):
            continue
        heart_rate = d.get("heart_rate") or {}
        sleep = d.get("sleep") or {}
        resting = heart_rate.get("resting_bpm")
        duration = sleep.get("total_duration_min")
        if isinstance(resting, (int, float)):
            resting_hrs.append(resting)
        if isinstance(duration, (int, float)):
            sleep_durations.append(duration)

    avg_resting_hr = round(statistics.mean(resting_hrs)) if resting_hrs else None
    avg_sleep_duration = round(statistics.mean(sleep_durations)) if sleep_durations else None

    # Upsert — replace if same user + week_start already exists
    existing = db.query(WearableHealthData).filter(
        WearableHealthData.user_id == current_user.user_id,
        WearableHealthData.week_start == week_start
    ).first()

    if existing:
        existing.week_end = week_end
        existing.avg_heart_rate = summary.get("avg_heart_rate_bpm")
        existing.avg_resting_hr = avg_resting_hr
        existing.total_calories = summary.get("total_kcal_burnt")
        existing.avg_spo2 = summary.get("avg_spo2_percent")
        existing.avg_sleep_quality = summary.get("avg_sleep_quality_score")
        existing.avg_sleep_duration_min = avg_sleep_duration
        existing.device = data.device
    else:
        record = WearableHealthData(
            user_id=current_user.user_id,
            week_start=week_start,
            week_end=week_end,
            avg_heart_rate=summary.get("avg_heart_rate_bpm"),
            avg_resting_hr=avg_resting_hr,
            total_calories=summary.get("total_kcal_burnt"),
            avg_spo2=summary.get("avg_spo2_percent"),
            avg_sleep_quality=summary.get("avg_sleep_quality_score"),
            avg_sleep_duration_min=avg_sleep_duration,
            device=data.device,
        )
        db.add(record)

    db.commit()
    return {"message": "Dữ liệu sức khỏe đã được lưu thành công."}


@router.get("/latest/me")
async def get_latest_wearable_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get latest wearable data for the authenticated user."""
    record = _get_latest_record_for_user(current_user.user_id, db)

    if not record:
        return {"hasData": False}

    return {
        "hasData": True,
        "heartRate": record.avg_heart_rate,
        "restingHR": record.avg_resting_hr,
        "calories": record.total_calories,
        "spo2": float(record.avg_spo2) if record.avg_spo2 else None,
        "sleepQuality": record.avg_sleep_quality,
        "sleepDurationMin": record.avg_sleep_duration_min,
        "device": record.device,
        "weekStart": str(record.week_start),
        "weekEnd": str(record.week_end),
    }


@router.get("/latest/{user_id}")
async def get_latest_wearable(user_id: UUID, db: Session = Depends(get_db)):
    record = _get_latest_record_for_user(user_id, db)

    if not record:
        return {"hasData": False}

    return {
        "hasData": True,
        "heartRate": record.avg_heart_rate,
        "restingHR": record.avg_resting_hr,
        "calories": record.total_calories,
        "spo2": float(record.avg_spo2) if record.avg_spo2 else None,
        "sleepQuality": record.avg_sleep_quality,
        "sleepDurationMin": record.avg_sleep_duration_min,
        "device": record.device,
        "weekStart": str(record.week_start),
        "weekEnd": str(record.week_end),
    }
