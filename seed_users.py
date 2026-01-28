from app import create_app
from models import db, User, Role
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    # ✅ Clear old users (safe since DB already cleaned)
    db.session.query(User).delete()
    db.session.commit()
    print("✅ Old users cleared")

    # ✅ Fresh new users
    users = [
        {
            "name": "Student",
            "email": "kalyandasari272@gmail.com",   # ✅ Your real email
            "phone": "+917036023547",               # ✅ Your real number
            "role": Role.STUDENT,
            "password": "1234"
        },
        {
            "name": "Incharge",
            "email": "incharge@mail.com",
            "phone": "+919999999999",               # dummy number
            "role": Role.INCHARGE,
            "password": "1234"
        },
        {
            "name": "HOD",
            "email": "hod@mail.com",
            "phone": "+918888888888",               # dummy
            "role": Role.HOD,
            "password": "1234"
        },
        {
            "name": "Security",
            "email": "security@mail.com",
            "phone": "+917777777777",               # dummy
            "role": Role.SECURITY,
            "password": "1234"
        }
    ]

    # ✅ Insert fresh users
    for u in users:
        user = User(
            name=u["name"],
            email=u["email"],
            phone=u["phone"],
            role=u["role"],
            password_hash=generate_password_hash(u["password"])
        )
        db.session.add(user)

    db.session.commit()

    print("\n✅✅ Fresh users created successfully!")
    print("--------------------------------------")
    for u in users:
        print(f"{u['role'].upper()} → {u['email']} | Password: {u['password']} | Phone: {u['phone']}")
