from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User model for authentication and basic user info"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship to UserProfile (one-to-one)
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Relationships to other models
    registrations = db.relationship('Registration', backref='user', lazy='dynamic')
    teams_as_captain = db.relationship('Team', backref='captain', lazy='dynamic')
    team_memberships = db.relationship('TeamMember', backref='user', lazy='dynamic')
    approved_payments = db.relationship('Payment', foreign_keys='Payment.approved_by', backref='approver', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_profile_complete(self):
        """Check if user profile is 100% complete"""
        if not self.profile:
            return False
        return self.profile.calculate_completion_percentage() == 100
    
    def get_verification_progress(self):
        """Get verification progress percentage (0-100)"""
        if not self.profile:
            return 0
        return self.profile.calculate_completion_percentage()


class UserProfile(db.Model):
    """Extended user profile information"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Personal information
    nama_lengkap = db.Column(db.String(100))
    sekolah = db.Column(db.String(100))
    kelas = db.Column(db.Integer)  # Grade (7, 8, or 9)
    nisn = db.Column(db.String(20))  # Student identification number
    
    # Contact information
    whatsapp = db.Column(db.String(20))
    instagram = db.Column(db.String(50))
    twitter = db.Column(db.String(50))
    
    # Document uploads
    foto_kartu_pelajar = db.Column(db.String(200))  # Student ID card photo
    screenshot_twibbon = db.Column(db.String(200))  # Twibbon screenshot
    
    # Verification status
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.nama_lengkap or "Incomplete"}>'
    
    def calculate_completion_percentage(self):
        """Calculate profile completion percentage based on required fields"""
        required_fields = [
            'nama_lengkap',
            'sekolah', 
            'kelas',
            'nisn',
            'whatsapp',
            'instagram',
            'foto_kartu_pelajar',
            'screenshot_twibbon'
        ]
        
        completed_fields = 0
        total_fields = len(required_fields)
        
        for field in required_fields:
            value = getattr(self, field)
            if value is not None and str(value).strip():
                completed_fields += 1
        
        percentage = int((completed_fields / total_fields) * 100)
        
        # Update verification_progress field
        self.verification_progress = percentage
        
        return percentage
    
    def get_missing_fields(self):
        """Get list of missing required fields with Indonesian labels"""
        field_labels = {
            'nama_lengkap': 'Nama Lengkap',
            'sekolah': 'Sekolah',
            'kelas': 'Kelas',
            'nisn': 'NISN',
            'whatsapp': 'Nomor WhatsApp',
            'instagram': 'Instagram',
            'foto_kartu_pelajar': 'Foto Kartu Pelajar',
            'screenshot_twibbon': 'Screenshot Twibbon'
        }
        
        missing_fields = []
        
        for field, label in field_labels.items():
            value = getattr(self, field)
            if value is None or not str(value).strip():
                missing_fields.append(label)
        
        return missing_fields
    
    def is_grade_eligible(self, min_grade=7, max_grade=9):
        """Check if user's grade is within eligible range"""
        if not self.kelas:
            return False
        return min_grade <= self.kelas <= max_grade
    
    def get_display_name(self):
        """Get display name for user"""
        return self.nama_lengkap or self.user.email.split('@')[0]