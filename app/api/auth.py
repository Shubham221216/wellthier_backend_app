from datetime import datetime, timedelta
import random
from app.models.nutritionist import Nutritionist
from app.models.referral import ClientNutritionistReferral
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user_authentication import UserAuthentication
from app.models.userProfile import Client
from app.config import settings
from app.core.email import send_otp_email
from app.models.user import OTP
from app.schemas.auth import *
from app.models.user_login_history import UserLoginHistory
from app.core.security import create_access_token, decode_access_token


router = APIRouter(prefix="/auth", tags=["auth"])

# Secret key for JWT from settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Utility to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

@router.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    """
    Step 1: Send OTP to email for verification.
    Only accepts email, does NOT create any user records yet.
    """
    data = await request.json()
    email = (data.get('email') or '').strip()
    
    if not email:
        raise HTTPException(status_code=400, detail='Email is required')
    
    # Check if user already exists
    if db.query(UserAuthentication).filter_by(loginid=email).first():
        raise HTTPException(status_code=400, detail='User already exists')
    
    if db.query(Client).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail='User already exists')

    # Generate and send OTP
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)
    otp_entry = OTP(username=email, otp_code=otp_code, expires_at=expires_at)
    db.add(otp_entry)
    db.commit()

    send_otp_email(email, otp_code, subject="Your Signup OTP")
    return {"msg": "OTP sent to email", "email": email}


@router.post("/verify-signup-otp")
async def verify_signup_otp(request: Request, db: Session = Depends(get_db)):
    """
    Step 2: Verify OTP - Just marks email as verified.
    Does NOT create any database records. User profile will be created in step 3.
    """
    from app.schemas.auth import OTPVerifyRequest
    
    data = await request.json()
    
    try:
        verify_req = OTPVerifyRequest(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Invalid request data: {str(e)}')
    
    email = verify_req.email.strip()
    otp_code = verify_req.otp.strip()

    # Verify OTP
    otp_entry = db.query(OTP).filter_by(username=email, otp_code=otp_code).first()
    if not otp_entry or otp_entry.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail='Invalid or expired OTP')

    # Clean up OTP
    db.delete(otp_entry)
    db.commit()

    # Return success - email verified (no token yet, no database records created)
    return {
        "msg": "Email verified successfully. Please complete your profile.",
        "email": email,
        "verified": True
    }



@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = (data.get('email') or '').strip()
    print("DEBUG >> login email:", email)   
    if not email:
        raise HTTPException(status_code=400, detail='Email is required')
    # Check existence via userauthentication table
    ua = db.query(UserAuthentication).filter_by(loginid=email).first()
    if not ua:
        raise HTTPException(status_code=404, detail='User not found')

    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)
    otp_entry = OTP(username=email, otp_code=otp_code, expires_at=expires_at)
    db.add(otp_entry)
    db.commit()

    # Send OTP email
    send_otp_email(email, otp_code, subject="Your Login OTP")
    return {"msg": "OTP sent to email"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/verify-login-otp")
async def verify_login_otp(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = (data.get('email') or '').strip()
    otp_code = (data.get('otp') or '').strip()

    if not email or not otp_code:
        raise HTTPException(status_code=400, detail='Email and OTP are required')

    # ✅ Validate OTP
    otp_entry = db.query(OTP).filter_by(username=email, otp_code=otp_code).first()
    print("Printing OTP Entry:", otp_entry)
    if not otp_entry or otp_entry.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail='Invalid or expired OTP')
    
    # ✅ Locate authentication row
    auth_record = db.query(UserAuthentication).filter_by(loginid=email).first()
    print("Printing auth_record:", auth_record)
    if not auth_record:
        raise HTTPException(status_code=404, detail='User not found')

    # ✅ Get corresponding user profile
    user_profile = db.query(Client).filter_by(userauthenticationid=auth_record.userauthenticationid).first()
    print("Printing User Profile >>", user_profile)
    if not user_profile:
        raise HTTPException(status_code=404, detail='User profile not found or something else')

    # ✅ Get IP and user-agent safely
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get('user-agent', 'unknown')

    # ✅ Record login history
    login_entry = UserLoginHistory(
        userid=user_profile.userid,
        login_time=datetime.now(),
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(login_entry)

    # ✅ Update last login timestamp
    user_profile.lastlogin = datetime.now()

    # ✅ Remove OTP
    db.delete(otp_entry)
    db.commit()

    # ✅ Generate JWT token
    token_data = {
        "auth_id": str(auth_record.userauthenticationid),
        "userid": str(user_profile.userid),
        "email": email,
        "role": "CLIENT"
    }
    token = create_access_token(token_data)

    return {"msg": "Login successful", "token": token}







@router.get("/me")
async def get_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        auth_id = int(payload.get("auth_id"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    auth_record = db.query(UserAuthentication).filter_by(userauthenticationid=auth_id).first()
    if not auth_record:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = db.query(Client).filter_by(userauthenticationid=auth_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Fetch linked nutritionist
    linkage = db.query(ClientNutritionistReferral).filter_by(userid=user_profile.userid).first()
    print("DEBUG >> linkage is:", linkage)

    nutritionist_id = linkage.nutritionist_id if linkage else None
    print("DEBUG >> nutritionist_id is:", nutritionist_id)

    nutritionist_data = None

    nutritionist = None

    if linkage and linkage.nutritionist_id:
        nutritionist = db.query(Nutritionist).filter_by(nutritionistid=linkage.nutritionist_id).first()
        if nutritionist:
            nutritionist_data = {
                "id": nutritionist.nutritionistid,
                "first_name": nutritionist.name,
                "email": nutritionist.email,
                "profile_photo": nutritionist.profilephoto,
                "organization": nutritionist.organisationphoto,
                "professionalTitle": nutritionist.professionaltitle,
                "phone": nutritionist.phone,
                "location": nutritionist.location,
                "website": nutritionist.website,
                "professionalBio": nutritionist.professionalbio,
                "referralcode": nutritionist.referralcode,
            }

    print("DEBUG >> nutritionist_data is:", nutritionist_data)


    user_data = {
        "id": user_profile.userid,
        "email": auth_record.loginid,
        "firstName": user_profile.name,
        "dob": user_profile.birthdate.isoformat() if getattr(user_profile, 'birthdate', None) else None,
        "mobile": getattr(user_profile, 'mobile', None),
        "gender": getattr(user_profile, 'gender', None),
        "height": getattr(user_profile, 'height', None),
        "weight": getattr(user_profile, 'weight', None),
        "Prime": getattr(user_profile, 'userplan', None),
        "city": getattr(user_profile, 'city', None),
        "state": getattr(user_profile, 'state', None),
        "country": getattr(user_profile, 'country', None),
        "pincode": getattr(user_profile, 'pin', None),
        "address": getattr(user_profile, 'address', None),
        "lastLogin": getattr(user_profile, 'lastlogin', None),
        "nutritionist_id": nutritionist_id, #linked nutritionist
        "referral": getattr(user_profile, 'referral', None),
        # "referred_by": getattr(nutritionist.name, 'referred_by', None),
        "referred_by": nutritionist.name if nutritionist else None,
        "startingweight": getattr(user_profile, 'startingweight', None),
        "targetweight": getattr(user_profile, 'targetweight', None),
    }

    return {"user": user_data, "nutritionist": nutritionist_data}

