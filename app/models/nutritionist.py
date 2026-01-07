# from sqlalchemy import Column, Integer, String, Text, LargeBinary
# from app.db.database import Base
# from sqlalchemy.orm import Session
# import random


# class Nutritionist(Base):
#     __tablename__ = 'nutritionist'

#     nutritionistid = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(50), nullable=False)
#     email = Column(String(50), nullable=False, unique=True)
#     password = Column(String(100), nullable=False)
#     profilephoto = Column(LargeBinary, nullable=True)
#     organisationphoto = Column(LargeBinary, nullable=True)
#     professionaltitle = Column(String(50), nullable=True)
#     phone = Column(String(15), nullable=True)
#     location = Column(String(100), nullable=True)
#     website = Column(String(100), nullable=True)
#     professionalbio = Column(Text, nullable=True)
#     referralcode = Column(String(10), nullable=True)

#     # Compatibility helpers
#     @property
#     def refer_code(self) -> str | None:
#         return self.referralcode


# def generate_refer_code() -> str:
#     """Generate a 6-digit numeric referral code as a string."""
#     return f"{random.randint(100000, 999999)}"


# def generate_unique_refer_code(db_session: Session) -> str:
#     """Generate a referral code and ensure uniqueness against nutritionist.referralcode.

#     Attempts up to 10 times before returning the last generated code.
#     """
#     code = generate_refer_code()
#     attempts = 0
#     while attempts < 10:
#         existing = db_session.query(Nutritionist).filter_by(referralcode=code).first()
#         if not existing:
#             return code
#         code = generate_refer_code()
#         attempts += 1
#     return code




from sqlalchemy import Column, Integer, String, Text, LargeBinary, Boolean, Date, Numeric
from app.db.database import Base
from sqlalchemy.orm import Session
import random


class Nutritionist(Base):
    __tablename__ = 'nutritionist'

    nutritionistid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    profilephoto = Column(LargeBinary, nullable=True)
    organisationphoto = Column(LargeBinary, nullable=True)
    professionaltitle = Column(String(50), nullable=True)
    phone = Column(String(15), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(100), nullable=True)
    professionalbio = Column(Text, nullable=True)

    referralcode = Column(String(10), nullable=True)

    is_active = Column(Boolean, default=True)
    account_status = Column(String(20), default="pending")

    gender = Column(String(10), nullable=True)
    dob = Column(Date, nullable=True)

    clinic = Column(String(150), nullable=True)
    experience = Column(Integer, nullable=True)
    specialization = Column(Text, nullable=True)
    education = Column(Text, nullable=True)

    license_no = Column(String(50), nullable=True)
    certificate_docs = Column(LargeBinary, nullable=True)

    revenue = Column(Numeric, default=0)
    subscription = Column(String(20), default="Premium")

    created_at = Column(Date, nullable=False)

    # Compatibility helper
    @property
    def refer_code(self) -> str | None:
        return self.referralcode


def generate_refer_code() -> str:
    """Generate a 6-digit numeric referral code as a string."""
    return f"{random.randint(100000, 999999)}"


def generate_unique_refer_code(db_session: Session) -> str:
    """Generate a referral code and ensure uniqueness against nutritionist.referralcode.

    Attempts up to 10 times before returning the last generated code.
    """
    code = generate_refer_code()
    attempts = 0
    while attempts < 10:
        existing = db_session.query(Nutritionist).filter_by(referralcode=code).first()
        if not existing:
            return code
        code = generate_refer_code()
        attempts += 1
    return code
