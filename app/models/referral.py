from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class ClientNutritionistReferral(Base):
    __tablename__ = "client_nutritionist_referral"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userid = Column(Integer, ForeignKey("userprofile.userid", ondelete="CASCADE"), nullable=False)
    nutritionist_id = Column(Integer, ForeignKey("nutritionist.nutritionistid", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
