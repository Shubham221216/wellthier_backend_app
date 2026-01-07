from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from app.db.database import Base

class SleepLog(Base):
    __tablename__ = "sleep_log"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("userprofile.userid", ondelete="CASCADE"), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    duration_minutes = Column(Integer, nullable=False)

    quality = Column(String(20), nullable=True)  # good / average / poor
    note = Column(String(160), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
