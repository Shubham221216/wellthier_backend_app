from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Time, Date, Boolean,
    DateTime, Numeric, ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base  # adapt import path

class UserWeightLog(Base):
    __tablename__ = 'user_weight_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey('userprofile.userid', ondelete='CASCADE'), nullable=False)
    weight = Column(Numeric(6,2), nullable=False)
    unit = Column(String(5), default='kg')
    entry_date = Column(Date, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
