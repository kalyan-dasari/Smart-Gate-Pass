from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    users = [
        User(
            name="Kalyan",
            email="kalyandasari272@gmail.com",
            phone="7036023547",
            role="student",
            password_hash=generate_password_hash("1234")
        ),
        User(
            name="Incharge Madam",
            email="incharge@mail.com",
            phone="9999999999",
            role="incharge",
            password_hash=generate_password_hash("1234")
        ),
        User(
            name="HOD Sir",
            email="hod@mail.com",
            phone="8888888888",
            role="hod",
            password_hash=generate_password_hash("1234")
        ),
        User(
            name="Security Guard",
            email="security@mail.com",
            phone="7777777777",
            role="security",
            password_hash=generate_password_hash("1234")
        )
    ]

    db.session.add_all(users)
    db.session.commit()

    print("✅ Initial users inserted successfully!")
