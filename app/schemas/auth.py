from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date


class ClientSignupRequest(BaseModel):
    # Step 1: Account Info
    fullName: str = Field(..., min_length=1, max_length=50)
    dateOfBirth: str  # Format: "YYYY-MM-DD"
    gender: str
    mobileNumber: str = Field(..., min_length=10, max_length=15)
    email: EmailStr
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pinCode: Optional[str] = None
    
    # Step 2: Health & Lifestyle
    healthGoal: Optional[str] = None
    height: Optional[float] = None
    heightUnit: Optional[str] = "cm"
    weight: Optional[float] = None
    weightUnit: Optional[str] = "kg"
    medicalCondition: Optional[List[str]] = None
    foodAllergies: Optional[List[str]] = None
    dietaryPreference: Optional[str] = None
    activityLevel: Optional[str] = None
    
    # Step 3: App Preferences
    preferredUnits: Optional[str] = "Metric ( Kg/Cm )"
    preferredLanguage: Optional[str] = "English"
    notificationConsent: Optional[bool] = True
    # Optional referral code supplied during signup (user-to-user referral)
    referCode: Optional[str] = None


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class LoginRequest(BaseModel):
    email: EmailStr


class LoginOTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
