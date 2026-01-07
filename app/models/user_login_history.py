from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, Text
from app.db.database import Base


class UserLoginHistory(Base):
    __tablename__ = "user_login_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("userprofile.userid", ondelete="CASCADE"))
    login_time = Column(DateTime, server_default=func.now())
    ip_address = Column(Text, nullable=True)  # To store IP address
    user_agent = Column(Text, nullable=True)  # To store User-Agent string
