import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

    # EMAIL
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # ✅ TWILIO (Matches your .env)
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_AUTH = os.getenv("TWILIO_AUTH")     # ✅ must match name in notify.py
    TWILIO_FROM = os.getenv("TWILIO_FROM")
