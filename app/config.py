from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None 
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_USE_TLS: Optional[bool] = None

    GOOGLE_REDIRECT_URI: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
