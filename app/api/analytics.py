# For Nutritionist use only - Analytics related endpoints
# Provides analytics on clients linked to a nutritionist
# Provide upcoming birthdays of clients
# Provide last login timestamps of clients

from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, text
from jose import jwt, JWTError
from app.db.database import SessionLocal

from app.models.referral import ClientNutritionistReferral
from app.models.userProfile import UserProfile
from app.models.user_login_history import UserLoginHistory
from app.schemas.referral import (
    NutritionistClientsWithAnalyticsResponse,
    UpcomingBirthdaysResponse,
)
from app.config import settings

router = APIRouter(prefix="/nutritionist/clients", tags=["Nutritionist Analytics"])

ALGORITHM = "HS256"
SECRET_KEY = settings.SECRET_KEY


# ✅ Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _decode_token(token: str) -> dict:
    """Decode JWT token using jose library"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def _get_token_payload(request: Request) -> dict:
    """Extract and decode token from Authorization header"""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth_header.split(" ", 1)[1].strip()
    return _decode_token(token)


def _require_nutritionist(payload: dict) -> int:
    """Extract nutritionist_id from token payload"""
    nutritionist_id = payload.get("nutritionist_id")
    if not nutritionist_id:
        raise HTTPException(status_code=401, detail="Invalid token: nutritionist_id missing")
    return int(nutritionist_id)


# ✅ Fetch clients & their last login with analytics
@router.get("/last-login", response_model=NutritionistClientsWithAnalyticsResponse)
async def get_clients_last_login(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Returns all clients linked to a nutritionist,
    along with their last login timestamps and engagement analytics.
    """
    # Extract and validate token
    payload = _get_token_payload(request)
    nutritionist_id = _require_nutritionist(payload)

    print(f"Nutritionist ID from token: {nutritionist_id}")

    # 1️⃣ Get referrals
    referrals = (
        db.query(ClientNutritionistReferral)
        .filter(ClientNutritionistReferral.nutritionist_id == nutritionist_id)
        .all()
    )

    if not referrals:
        return NutritionistClientsWithAnalyticsResponse(
            nutritionist_id=nutritionist_id,
            total_clients=0,
            clients=[],
            analytics={
                "overview": [
                    {"label": "Daily Active", "value": 0},
                    {"label": "Weekly Active", "value": 0},
                    {"label": "Monthly Retention", "value": 0},
                ],
                "hourlyBreakdown": [],
                "peakHours": {"range": None, "login_count": 0},
            },
            msg="No referrals found for this nutritionist."
        )

    client_ids = [r.userid for r in referrals]

    # 2️⃣ Fetch user + last login using MAX(login_time)
    subquery = (
        db.query(
            UserLoginHistory.userid,
            func.max(UserLoginHistory.login_time).label("last_login")
        )
        .filter(UserLoginHistory.userid.in_(client_ids))
        .group_by(UserLoginHistory.userid)
        .subquery()
    )

    # 3️⃣ Join with user profile
    clients = (
        db.query(UserProfile, subquery.c.last_login)
        .join(subquery, UserProfile.userid == subquery.c.userid, isouter=True)
        .filter(UserProfile.userid.in_(client_ids))
        .all()
    )

    # 4️⃣ Map results
    client_list = []
    for c in clients:
        if hasattr(c, 'UserProfile'):
            # Result from join query
            user = c.UserProfile
            last_login = c.last_login
        else:
            # Direct UserProfile object
            user = c
            last_login = None
        
        client_list.append({
            "userid": user.userid,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "lastLogin": last_login.isoformat() if last_login else None,
        })

    # ✅ Compute analytics stats from login history
    seven_days_ago = datetime.now() - timedelta(days=7)
    thirty_days_ago = datetime.now() - timedelta(days=30)

    total_clients = len(client_ids)

    # Count how many unique clients logged in recently
    daily_active = (
        db.query(func.count(func.distinct(UserLoginHistory.userid)))
        .filter(
            UserLoginHistory.userid.in_(client_ids),
            func.date(UserLoginHistory.login_time) == datetime.now().date()
        )
        .scalar() or 0
    )

    weekly_active = (
        db.query(func.count(func.distinct(UserLoginHistory.userid)))
        .filter(
            UserLoginHistory.userid.in_(client_ids),
            UserLoginHistory.login_time >= seven_days_ago
        )
        .scalar() or 0
    )

    monthly_retention = (
        db.query(func.count(func.distinct(UserLoginHistory.userid)))
        .filter(
            UserLoginHistory.userid.in_(client_ids),
            UserLoginHistory.login_time >= thirty_days_ago
        )
        .scalar() or 0
    )

    # Compute logins per weekday (Mon, Tue, ...)
    weekday_counts = (
        db.query(
            extract("dow", UserLoginHistory.login_time).label("day"),
            func.count().label("count")
        )
        .filter(UserLoginHistory.userid.in_(client_ids))
        .group_by("day")
        .order_by("day")
        .all()
    )

    weekday_map = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hourly_breakdown = [
        {"label": weekday_map[int(d)], "value": count} for d, count in weekday_counts
    ]

    # 6️⃣ ✅ Single peak hour range (2-hour window)
    peak_hour_query = text("""
        SELECT
            FLOOR(EXTRACT(HOUR FROM login_time) / 2) * 2 AS hour_start,
            COUNT(*) AS login_count
        FROM user_login_history
        WHERE userid = ANY(:client_ids)
        GROUP BY hour_start
        ORDER BY login_count DESC
        LIMIT 1
    """)

    peak_result = db.execute(peak_hour_query, {"client_ids": client_ids}).fetchone()

    def format_hour_range(hour_start):
        hour_end = (hour_start + 2) % 24
        def format_ampm(h):
            ampm = "AM" if h < 12 else "PM"
            hour_12 = h % 12 or 12
            return f"{hour_12}{ampm}"
        return f"{format_ampm(hour_start)}–{format_ampm(hour_end)}"

    if peak_result:
        peak_hours = {
            "range": format_hour_range(int(peak_result.hour_start)),
            "login_count": peak_result.login_count
        }
    else:
        peak_hours = {"range": None, "login_count": 0}

    print(f"Client list: {client_list}")
    print(f"Analytics - Daily: {daily_active}, Weekly: {weekly_active}, Monthly: {monthly_retention}")

    # ✅ Final response payload (frontend-ready)
    return {
        "nutritionist_id": nutritionist_id,
        "total_clients": total_clients,
        "clients": client_list,
        "analytics": {
            "overview": [
                {"label": "Daily Active", "value": daily_active},
                {"label": "Weekly Active", "value": weekly_active},
                {"label": "Monthly Retention", "value": monthly_retention},
            ],
            "hourlyBreakdown": hourly_breakdown,
            "peakHours": peak_hours,
        },
    }


@router.get("/upcoming-birthdays", response_model=UpcomingBirthdaysResponse)
async def get_upcoming_birthdays(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Returns clients with birthdays in the next 7 days.
    """
    # Extract and validate token
    payload = _get_token_payload(request)
    nutritionist_id = _require_nutritionist(payload)
    
    today = date.today()

    # Fetch linked client IDs for the given nutritionist
    client_ids = (
        db.query(ClientNutritionistReferral.userid)
        .filter(ClientNutritionistReferral.nutritionist_id == nutritionist_id)
        .all()
    )
    client_ids = [c[0] for c in client_ids]

    if not client_ids:
        return {"nutritionist_id": nutritionist_id, "total_upcoming_birthdays": 0, "upcoming_birthdays": []}

    # Fetch clients
    clients = db.query(
        UserProfile.userid,
        UserProfile.name,
        UserProfile.email,
        UserProfile.mobile,
        UserProfile.birthdate
    ).filter(UserProfile.userid.in_(client_ids)).all()

    upcoming_birthdays = []
    for c in clients:
        if not c.birthdate:
            continue
            
        bday = c.birthdate
        # Normalize birthday to this year
        this_year_bday = bday.replace(year=today.year)

        # If birthday has passed this year, move to next year
        if this_year_bday < today:
            this_year_bday = this_year_bday.replace(year=today.year + 1)

        days_remaining = (this_year_bday - today).days

        # ✅ Include all birthdays within next 7 days
        if 0 <= days_remaining <= 7:
            upcoming_birthdays.append({
                "userid": c.userid,
                "name": c.name,
                "email": c.email,
                "mobile": c.mobile,
                "birthdate": c.birthdate.isoformat() if c.birthdate else None,
                "days_remaining": days_remaining
            })

    # ✅ Sort by days_remaining so nearest birthdays appear first
    upcoming_birthdays.sort(key=lambda x: x["days_remaining"])

    return {
        "nutritionist_id": nutritionist_id,
        "total_upcoming_birthdays": len(upcoming_birthdays),
        "upcoming_birthdays": upcoming_birthdays
    }
