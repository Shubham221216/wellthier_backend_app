from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from app.db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = 'users'
   
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)  # Use Text, handle case-insensitivity in queries
    phone = Column(Text, unique=True)
    password_hash = Column(Text)
    role = Column(String(50), nullable=False)  # Store role as varchar
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class OTP(Base):
    __tablename__ = 'otp'
   
    id = Column(Integer, primary_key=True)
    username = Column(String(150), nullable=False)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
