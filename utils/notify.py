from flask_mail import Message
from config import Config
from flask import current_app
from twilio.rest import Client

def send_email(subject, recipients, body):
    try:
        mail_ext = current_app.extensions.get('mail')
        if not mail_ext:
            print("❌ Email error: Flask-Mail extension is not initialized")
            return False

        with mail_ext.connect() as conn:
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
