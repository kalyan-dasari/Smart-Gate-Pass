import os
from dotenv import load_dotenv

load_dotenv()


def _to_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean(value):
    return value.strip() if isinstance(value, str) else value

class Config:
    SECRET_KEY = _clean(os.getenv("SECRET_KEY"))
    SQLALCHEMY_DATABASE_URI = _clean(os.getenv("DATABASE_URI"))

    # EMAIL
    MAIL_SERVER = _clean(os.getenv("MAIL_SERVER"))
    MAIL_PORT = _to_int(os.getenv("MAIL_PORT"), 587)
    MAIL_USE_TLS = _to_bool(os.getenv("MAIL_USE_TLS"), True)
    MAIL_USE_SSL = _to_bool(os.getenv("MAIL_USE_SSL"), False)
    MAIL_USERNAME = _clean(os.getenv("MAIL_USERNAME"))
    MAIL_PASSWORD = _clean(os.getenv("MAIL_PASSWORD"))
    MAIL_DEFAULT_SENDER = _clean(os.getenv("MAIL_DEFAULT_SENDER"))

    # Gmail app passwords are often copied with spaces, normalize once.
    if MAIL_SERVER and "gmail" in MAIL_SERVER.lower() and MAIL_PASSWORD:
        MAIL_PASSWORD = MAIL_PASSWORD.replace(" ", "")

    # ✅ TWILIO (Matches your .env)
    TWILIO_SID = _clean(os.getenv("TWILIO_SID"))
    TWILIO_AUTH = _clean(os.getenv("TWILIO_AUTH"))     # ✅ must match name in notify.py
    TWILIO_FROM = _clean(os.getenv("TWILIO_FROM"))
