import smtplib
from email.mime.text import MIMEText
from app.config import settings

def send_otp_email(to_email: str, otp_code: str, subject: str = "Your OTP"):
    msg = MIMEText(f"Your OTP is: {otp_code}")
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_USERNAME
    msg["To"] = to_email

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(settings.MAIL_USERNAME, [to_email], msg.as_string())