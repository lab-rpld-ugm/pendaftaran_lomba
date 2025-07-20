from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.masuk'
    login_manager.login_message = 'Silakan masuk untuk mengakses halaman ini.'
    login_manager.login_message_category = 'info'
    
    # Import models after app initialization to avoid circular imports
    from app.models import (
        User, UserProfile, Competition, CompetitionCategory,
        Registration, IndividualRegistration, TeamRegistration,
        Team, TeamMember, Payment
    )
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.blueprints.competition import bp as competition_bp
    app.register_blueprint(competition_bp, url_prefix='/kompetisi')
    
    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.blueprints.team import bp as team_bp
    app.register_blueprint(team_bp)
    
    from app.blueprints.payment import bp as payment_bp
    app.register_blueprint(payment_bp)
    
    from app.blueprints.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    # Template context processors and global functions
    @app.context_processor
    def inject_verification_utilities():
        """Make verification utilities available in all templates"""
        from app.utils.verification import ProfileVerificationHelper, check_competition_eligibility
        return {
            'ProfileVerificationHelper': ProfileVerificationHelper,
            'check_competition_eligibility': check_competition_eligibility
        }
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app