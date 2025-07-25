from flask import Flask, request
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
    
    # Configure app for iframe usage
    @app.after_request
    def after_request(response):
        # Allow iframe embedding from specific domains
        allowed_origins = [
            'https://pdc.praditadirgantara.sch.id',
            'http://localhost:3000',  # For local testing
            'http://127.0.0.1:3000'   # For local testing
        ]
        
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        
        # Check if request is from allowed origin
        if origin in allowed_origins or any(allowed in (referer or '') for allowed in allowed_origins):
            response.headers['Access-Control-Allow-Origin'] = origin or 'https://pdc.praditadirgantara.sch.id'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        # Remove X-Frame-Options to allow iframe embedding
        response.headers.pop('X-Frame-Options', None)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Set SameSite cookie attributes for iframe support
        if 'Set-Cookie' in response.headers:
            cookies = response.headers.getlist('Set-Cookie')
            response.headers.clear()
            for cookie in cookies:
                # Parse cookie to modify attributes
                cookie_parts = cookie.split(';')
                cookie_base = cookie_parts[0]
                
                # Remove existing SameSite and Secure attributes
                filtered_parts = [cookie_base]
                for part in cookie_parts[1:]:
                    part = part.strip()
                    if not part.lower().startswith('samesite') and not part.lower().startswith('secure'):
                        filtered_parts.append(part)
                
                # Always add SameSite=None for iframe compatibility
                filtered_parts.append('SameSite=None')
                
                # Add Secure flag - required for SameSite=None and HTTPS
                filtered_parts.append('Secure')
                
                # Reconstruct cookie
                new_cookie = '; '.join(filtered_parts)
                response.headers.add('Set-Cookie', new_cookie)
        
        return response
    
    # Custom CSRF token generation for iframe support
    from flask_wtf.csrf import generate_csrf
    
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)
    
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

    @app.context_processor
    def inject_utility_functions():
        return dict(min=min)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app