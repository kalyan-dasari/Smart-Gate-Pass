from flask_mail import Message
from config import Config
from flask import current_app
from twilio.rest import Client
import smtplib

def send_email(subject, recipients, body):
    try:
        mail_ext = current_app.extensions.get('mail')
        if not mail_ext:
            print("❌ Email error: Flask-Mail extension is not initialized")
            return False

        if not (Config.MAIL_SERVER and Config.MAIL_PORT and Config.MAIL_USERNAME and Config.MAIL_PASSWORD):
            print("❌ Email error: Mail configuration is incomplete")
            return False

        recipient_list = recipients if isinstance(recipients, list) else [recipients]

        with mail_ext.connect() as conn:
            msg = Message(
                subject,
                recipients=recipient_list,
                body=body,
                sender=Config.MAIL_DEFAULT_SENDER
            )
            conn.send(msg)
        print("✅ Email sent to:", recipient_list)
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Email error: Gmail rejected credentials. Use a Gmail App Password (16 chars), remove spaces, and enable 2-Step Verification.")
        return False

    except Exception as e:
        print("❌ Email error:", e)
        return False


def send_sms(to_number, message):
    try:
        if not (Config.TWILIO_SID and Config.TWILIO_AUTH and Config.TWILIO_FROM):
            print("❌ SMS error: Twilio credentials missing")
            return False

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
