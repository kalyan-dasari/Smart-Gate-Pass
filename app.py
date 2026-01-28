from flask import Flask, redirect, url_for
from config import Config
from models import db
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    mail = Mail(app)

    # load user function
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="localhost", port=5000, debug=True)
