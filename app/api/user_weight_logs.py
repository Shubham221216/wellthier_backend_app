from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.userProfile import UserProfile
from app.models.user_weight_logs import UserWeightLog
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from app.schemas.weight_log import WeightUpdateRequest
from decimal import Decimal

router = APIRouter(prefix="/weight-log", tags=["Weight Log"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def log_weight(
    userid: int = Query(..., description="User ID"),
    weight: float = Query(..., description="Weight value"),
    unit: str = Query("kg", description="kg or lbs"),
    db: Session = Depends(get_db)
):
    print(f"Logging weight for user ID: {userid}, weight: {weight}, unit: {unit}")

    entry = UserWeightLog(
        userid=userid,
        weight=weight,
        unit=unit.lower(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "userid": entry.userid, "weight": float(entry.weight), "unit": entry.unit, "entry_date": entry.entry_date}




@router.get("/logs")
def get_weight_logs(
    userid: int = Query(...),
    mode: str = Query("daily", enum=["daily", "weekly", "monthly"]),
    db: Session = Depends(get_db)
):
    if userid is None:
        raise HTTPException(status_code=400, detail="userid required")

    now = datetime.now().date()

    # ---- DAILY MODE ----
    if mode == "daily":
        raw_logs = db.query(UserWeightLog).filter(
            UserWeightLog.userid == userid,
            UserWeightLog.entry_date >= now - timedelta(days=5)
        ).order_by(UserWeightLog.entry_date.desc(), UserWeightLog.created_at.desc()).all()

        # Keep only the most recently updated entry per day
        latest_per_day = {}
        for log in raw_logs:
            if log.entry_date not in latest_per_day:
                latest_per_day[log.entry_date] = log  # first encounter = latest update of that day

        # Build 5 calendar days response (include missing days)
        daily_response = []
        for i in range(4, -1, -1):  # 4 days ago → today = 5 entries total
            day = now - timedelta(days=i)
            if day in latest_per_day:
                log = latest_per_day[day]
                daily_response.append({
                    "date": day.isoformat(),
                    "weight": float(log.weight),
                    "unit": log.unit,
                    "created_at": log.created_at.isoformat()
                })
            else:
                daily_response.append({
                    "date": day.isoformat(),
                    "weight": None,
                    "unit": None,
                    "created_at": None
                })

        # Extract only filled weights for calculation
        avg_values = [d["weight"] for d in daily_response if d["weight"] is not None]
        if not avg_values:
            return {"userid": userid, "mode": mode, "logs": daily_response}

        values = avg_values
        logs = daily_response

    # ---- WEEKLY MODE ----
    elif mode == "weekly":
        raw_logs = db.query(UserWeightLog).filter(
            UserWeightLog.userid == userid,
            UserWeightLog.entry_date >= now - timedelta(days=28)
        ).all()

        weekly_response = []
        for i in range(4):
            w_start = now - timedelta(days=7 * (3-i))
            w_end = w_start + timedelta(days=6)

            week_values = [
                float(l.weight) for l in raw_logs
                if w_start <= l.entry_date <= w_end
            ]

            avg_w = round(sum(week_values)/len(week_values), 2) if week_values else None
            print(f"Week {w_start} to {w_end}: values={week_values} avg={avg_w}")

            weekly_response.append({
                "week_start": w_start.isoformat(),
                "avg_weight": avg_w
            })

        calc_weeks = [w["avg_weight"] for w in weekly_response if w["avg_weight"] is not None]
        if not calc_weeks:
            return {"userid": userid, "mode": mode, "logs": weekly_response}

        values = calc_weeks
        logs = weekly_response

    # ---- MONTHLY MODE ----
    else:  # monthly
        raw_logs = db.query(UserWeightLog).filter(
            UserWeightLog.userid == userid,
            UserWeightLog.entry_date >= now - relativedelta(months=4)
        ).all()

        monthly_response = []
        for i in range(4):
            m_start = now - relativedelta(months=3-i)
            m_key = m_start.strftime("%Y-%m")

            month_values = [
                float(l.weight) for l in raw_logs
                if m_key == l.entry_date.strftime("%Y-%m")
            ]

            avg_m = round(sum(month_values)/len(month_values), 2) if month_values else None

            monthly_response.append({
                "month": m_key,
                "avg_weight": avg_m
            })

        calc_months = [m["avg_weight"] for m in monthly_response if m["avg_weight"] is not None]
        if not calc_months:
            return {"userid": userid, "mode": mode, "logs": monthly_response}

        values = calc_months
        logs = monthly_response

    # ---- COMMON CALCULATIONS BASED ON AVERAGES ----
    first_w, latest_w = values[0], values[-1]
    diff = latest_w - first_w

    trend = "stable"
    if diff > 0:
        trend = "up"
    elif diff < 0:
        trend = "down"

    min_w, max_w = min(values), max(values)

    # ---- Optional BMI ----
    user = db.query(UserProfile).filter(UserProfile.userid == userid).first()
    bmi = float(user.bmi) if user and user.bmi is not None else None

    # ---- Final Response ----
    return {
        "userid": userid,
        "mode": mode,
        "bmi": bmi,
        "min_weight": min_w,
        "max_weight": max_w,
        "weight_diff": diff,
        "trend": trend,
        "logs": logs
    }





@router.put("/user/{userid}/weight-target")
def update_start_and_target_weight(
    userid: int,
    data: WeightUpdateRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserProfile).filter(UserProfile.userid == userid).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Validate numeric values if provided
    if data.startingweight is not None:
        # if not isinstance(data.startingweight, (int, float)):
        #     raise HTTPException(status_code=400, detail="startingweight must be numeric")
        user.startingweight = data.startingweight

    if data.targetweight is not None:
        # if not isinstance(data.targetweight, (int, float)):
        #     raise HTTPException(status_code=400, detail="targetweight must be numeric")
        user.targetweight = data.targetweight

    # ✅ Validate unit if provided
    if data.unit:
        u = data.unit.lower()
        if u not in ["kg", "lbs"]:
            raise HTTPException(status_code=400, detail="unit must be kg or lbs")
        user.weight_unit = u  # save normalized unit if you store it in profile

    # ✅ Commit changes
    db.commit()
    db.refresh(user)

    return {
        "message": "Starting Weight and Target Weight updated successfully ✅",
        "userid": user.userid,
        "startingweight": float(user.startingweight) if user.startingweight else None,
        "targetweight": float(user.targetweight) if user.targetweight else None,
        "unit": user.weight_unit if hasattr(user, "weight_unit") else "kg"
    }
