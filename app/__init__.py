from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.hr import hr_bp
    from .routes.employee import employee_bp
    from .routes.attendance import attendance_bp
    from .routes.leave import leave_bp
    from .routes.payroll import payroll_bp
    from .routes.reports import reports_bp
    from .routes.documents import documents_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(hr_bp, url_prefix='/hr')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(leave_bp, url_prefix='/leave')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(documents_bp, url_prefix='/documents')

    return app
