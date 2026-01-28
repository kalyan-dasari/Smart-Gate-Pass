from flask_mail import Message
from config import Config
from flask import current_app
from twilio.rest import Client

def send_email(subject, recipients, body):
    try:
        with current_app.extensions['mail'].connect() as conn:
            msg = Message(
                subject,
                recipients=[recipients],
                body=body,
                sender=Config.MAIL_DEFAULT_SENDER
            )
            conn.send(msg)
        print("✅ Email sent to:", recipients)
        return True

    except Exception as e:
        print("❌ Email error:", e)
        return False


def send_sms(to_number, message):
    try:
        client = Client(
            Config.TWILIO_SID,
            Config.TWILIO_AUTH
        )
        client.messages.create(
            body=message,
            from_=Config.TWILIO_FROM,
            to=to_number
        )
        print("✅ SMS sent to:", to_number)
        return True

    except Exception as e:
        print("❌ SMS error:", e)
        return False
