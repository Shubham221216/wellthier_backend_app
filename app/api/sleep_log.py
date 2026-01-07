from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from app.db.database import SessionLocal
from app.models.sleep_log import SleepLog
from app.schemas.sleep_log import (
    SleepLogCreate,
    SleepLogResponse,
    SleepSummaryResponse
)
from app.utils.sleep import calculate_sleep_minutes

router = APIRouter(prefix="/sleep-log", tags=["Sleep Log"])


# ✅ Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create Sleep Log
@router.post("", response_model=SleepLogResponse)
def create_sleep_log(
    userid: int,
    data: SleepLogCreate,
    db: Session = Depends(get_db)
):
    duration = calculate_sleep_minutes(data.start_time, data.end_time)

    log = SleepLog(
        userid=userid,
        start_time=data.start_time,
        end_time=data.end_time,
        duration_minutes=duration,
        quality=data.quality,
        note=data.note
    )

    db.add(log)
    db.commit()
    db.refresh(log)
    return log

# Get Latest Sleep Log
@router.get("/latest")
def get_latest_sleep(userid: int, db: Session = Depends(get_db)):
    log = (
        db.query(SleepLog)
        .filter(SleepLog.userid == userid)
        .order_by(SleepLog.end_time.desc())
        .first()
    )

    if not log:
        return {
            "date": None,
            "minutes": 0
        }

    return {
        "date": log.end_time.date().isoformat(),
        "minutes": log.duration_minutes,
        "start_time": log.start_time.time(),
        "end_time": log.end_time.time(),
        "quality": log.quality
    }


# Get Sleep Summary 
@router.get("/summary", response_model=SleepSummaryResponse)
def get_sleep_summary(
    userid: int,
    mode: str = Query("daily", enum=["daily", "weekly", "monthly"]),
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()

    if mode == "daily":
        start = now - timedelta(days=6)

        rows = (
            db.query(
                func.date(SleepLog.start_time).label("label"),
                func.sum(SleepLog.duration_minutes).label("minutes")
            )
            .filter(
                SleepLog.userid == userid,
                SleepLog.start_time >= start
            )
            .group_by("label")
            .order_by("label")
            .all()
        )

        labels = [r.label.strftime("%a") for r in rows]
        values = [r.minutes for r in rows]

    elif mode == "weekly":
        start = now - timedelta(weeks=4)

        rows = (
            db.query(
                func.date_trunc("week", SleepLog.start_time).label("label"),
                func.sum(SleepLog.duration_minutes).label("minutes")
            )
            .filter(
                SleepLog.userid == userid,
                SleepLog.start_time >= start
            )
            .group_by("label")
            .order_by("label")
            .all()
        )

        labels = [f"Week {i+1}" for i in range(len(rows))]
        values = [r.minutes for r in rows]

    else:  # monthly
        start = now - timedelta(days=120)

        rows = (
            db.query(
                func.date_trunc("month", SleepLog.start_time).label("label"),
                func.sum(SleepLog.duration_minutes).label("minutes")
            )
            .filter(
                SleepLog.userid == userid,
                SleepLog.start_time >= start
            )
            .group_by("label")
            .order_by("label")
            .all()
        )

        labels = [r.label.strftime("%b") for r in rows]
        values = [r.minutes for r in rows]

    return {
        "mode": mode,
        "labels": labels,
        "values": values
    }


@router.delete("/{sleep_id}")
def delete_sleep_log(sleep_id: int, db: Session = Depends(get_db)):
    log = db.query(SleepLog).filter(SleepLog.id == sleep_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")

    db.delete(log)
    db.commit()
    return {"message": "Sleep log deleted"}
