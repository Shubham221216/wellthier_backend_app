from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ClientBasic(BaseModel):
    userid: int
    name: str
    email: str
    mobile: Optional[str] = None

    class Config:
        orm_mode = True


class ClientWithLogin(BaseModel):
    userid: int
    name: str
    email: str
    mobile: Optional[str] = None
    lastLogin: Optional[str] = None  # ISO format datetime string

    class Config:
        orm_mode = True


class OverviewItem(BaseModel):
    label: str
    value: int


class HourlyBreakdownItem(BaseModel):
    label: str  # Mon, Tue, Wed, etc.
    value: int


class PeakHours(BaseModel):
    range: Optional[str] = None  # e.g., "6PM–8PM"
    login_count: int = 0


class AnalyticsData(BaseModel):
    overview: List[OverviewItem]
    hourlyBreakdown: List[HourlyBreakdownItem]
    peakHours: PeakHours


class NutritionistClientsResponse(BaseModel):
    nutritionist_id: int
    total_clients: int
    clients: List[ClientBasic]


class NutritionistClientsWithAnalyticsResponse(BaseModel):
    nutritionist_id: int
    total_clients: int
    clients: List[ClientWithLogin]
    analytics: AnalyticsData
    msg: Optional[str] = None


class UpcomingBirthday(BaseModel):
    userid: int
    name: str
    email: str
    mobile: Optional[str] = None
    birthdate: Optional[str] = None  # Date string
    days_remaining: int


class UpcomingBirthdaysResponse(BaseModel):
    nutritionist_id: int
    total_upcoming_birthdays: int
    upcoming_birthdays: List[UpcomingBirthday]
