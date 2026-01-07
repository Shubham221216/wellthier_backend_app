from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ---------- Create / Update ----------
class SleepLogCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    quality: Optional[str] = None
    note: Optional[str] = None


# ---------- Single Log ----------
class SleepLogResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    quality: Optional[str]
    note: Optional[str]

    class Config:
        from_attributes = True


# ---------- Chart / Summary ----------
class SleepSummaryResponse(BaseModel):
    mode: str
    labels: List[str]
    values: List[int]
