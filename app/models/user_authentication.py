from sqlalchemy import Column, Integer, String
from app.db.database import Base


class UserAuthentication(Base):
    __tablename__ = "userauthentication"

    userauthenticationid = Column(Integer, primary_key=True, autoincrement=True)
    loginid = Column(String(75), nullable=True)