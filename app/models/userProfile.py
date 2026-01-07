
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, Boolean, ForeignKey, ARRAY
from sqlalchemy.sql import func, text
from app.db.database import Base


class UserProfile(Base):
    __tablename__ = 'userprofile'

    userid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    birthdate = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    mobile = Column(String(10), nullable=False)
    email = Column(String(50), nullable=False)
    address = Column(String(150), nullable=True)
    city = Column(String(30), nullable=True)
    state = Column(String(30), nullable=True)
    country = Column(String(30), nullable=True)
    pin = Column(Integer, nullable=True)
    height = Column(Numeric(5, 2), nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    bmi = Column(Numeric(5, 2), nullable=True)  # Added BMI column
    unitofmeasure = Column(String(15), nullable=True)
    preferredlanguage = Column(String(25), nullable=True)
    referral = Column(String(20), nullable=True)
    userplan = Column(String(50), nullable=True)
    notificationopted = Column(String(5), nullable=True)
    mealplanid = Column(Integer, nullable=True)
    subscriptionplanid = Column(Integer, nullable=True)
    nutritionistid = Column(Integer, nullable=True)
    userauthenticationid = Column(Integer, ForeignKey('userauthentication.userauthenticationid', ondelete='CASCADE'), nullable=True)
    lastlogin = Column(DateTime)

    
    # Health and Lifestyle fields
    healthgoal = Column(String(50), nullable=True)
    heightunit = Column(String(10), nullable=True, default='cm')
    weightunit = Column(String(10), nullable=True, default='kg')
    medicalconditions = Column(ARRAY(Text), nullable=True)
    foodallergies = Column(ARRAY(Text), nullable=True)
    dietarypreference = Column(String(30), nullable=True)
    activitylevel = Column(String(30), nullable=True)
    startingweight = Column(Numeric(5, 2), nullable=True)
    targetweight = Column(Numeric(5, 2), nullable=True)



# Backwards-compat alias so existing imports continue to work
Client = UserProfile