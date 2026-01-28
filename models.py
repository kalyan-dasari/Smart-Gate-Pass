from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Role:
    STUDENT = 'student'
    INCHARGE = 'incharge'
    HOD = 'hod'
    SECURITY = 'security'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)   # ✅ ADD THIS LINE
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), default=Role.STUDENT)
    department = db.Column(db.String(64), nullable=True)

    gatepasses = db.relationship('GatePass', backref='student', lazy=True)



class GatePass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    reason = db.Column(db.Text, nullable=False)
    from_time = db.Column(db.String(50), nullable=True)
    to_time = db.Column(db.String(50), nullable=True)
    parent_contact = db.Column(db.String(20), nullable=True)

    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    
    # pending_incharge -> pending_hod -> approved -> scanned_exit -> scanned_entry
    status = db.Column(db.String(32), default='pending_incharge')

    incharge_remarks = db.Column(db.Text, nullable=True)
    hod_remarks = db.Column(db.Text, nullable=True)

    qr_code_filename = db.Column(db.String(200), nullable=True)

    exit_time = db.Column(db.DateTime, nullable=True)
    entry_time = db.Column(db.DateTime, nullable=True)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200))
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
