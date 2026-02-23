from flask import Flask, redirect, url_for
from config import Config
from models import db, Role
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from datetime import datetime

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    @app.template_filter('dt_short')
    def dt_short(value):
        if not value:
            return '-'
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M')
        return str(value)

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    Mail(app)

    # load user function
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.approver import approver_bp
    from routes.security import security_bp
    from routes.incharge import incharge_bp
    from routes.hod import hod_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(approver_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(incharge_bp)
    app.register_blueprint(hod_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == Role.STUDENT:
                return redirect(url_for('student.dashboard'))
            if current_user.role == Role.INCHARGE:
                return redirect(url_for('incharge.dashboard'))
            if current_user.role == Role.HOD:
                return redirect(url_for('hod.dashboard'))
            if current_user.role == Role.SECURITY:
                return redirect(url_for('security.scan_page'))
        return redirect(url_for('auth.login'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="localhost", port=5000, debug=True)
