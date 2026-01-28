from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Role
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful')
            # return redirect(url_for('student.dashboard'))
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'incharge':
                return redirect(url_for('incharge.dashboard'))
            elif user.role == 'hod':
                return redirect(url_for('hod.dashboard'))
            elif user.role == 'security':
                return redirect(url_for('security.scan_page'))
            else:
                return redirect(url_for('auth.login'))


        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    # Simple register for testing — in production restrict registration
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        role = request.form.get('role', Role.STUDENT)
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))
        user = User(name=name, email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash('User registered, please login', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))
