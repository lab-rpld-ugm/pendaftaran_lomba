from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from app import db


class Competition(db.Model):
    """Competition model with pricing and deadline management"""
    __tablename__ = 'competitions'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_kompetisi = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)
    
    # Competition type and category
    kategori = db.Column(db.String(50), nullable=False)  # 'individual' or 'team'
    jenis = db.Column(db.String(50), nullable=False)  # 'academic', 'creative', 'performance', 'basketball', 'esports'
    
    # Pricing information
    harga_early_bird = db.Column(db.Integer, nullable=False)  # Early bird price in rupiah
    harga_reguler = db.Column(db.Integer, nullable=False)  # Regular price in rupiah
    
    # Date management
    tanggal_mulai_early_bird = db.Column(db.DateTime, nullable=False)
    tanggal_akhir_early_bird = db.Column(db.DateTime, nullable=False)
    deadline_registrasi = db.Column(db.DateTime, nullable=False)
    tanggal_kompetisi = db.Column(db.DateTime, nullable=False)
    
    # Grade eligibility
    min_kelas = db.Column(db.Integer, default=7, nullable=False)
    max_kelas = db.Column(db.Integer, default=9, nullable=False)
    
    # Team size constraints (for team competitions)
    min_anggota = db.Column(db.Integer)  # Minimum team members
    max_anggota = db.Column(db.Integer)  # Maximum team members
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('Registration', backref='competition', lazy='dynamic')
    teams = db.relationship('Team', backref='competition', lazy='dynamic')
    
    def __repr__(self):
        return f'<Competition {self.nama_kompetisi}>'
    
    def get_current_price(self):
        """Get current price based on early bird status"""
        if self.is_early_bird_active():
            return self.harga_early_bird
        return self.harga_reguler
    
    def is_early_bird_active(self):
        """Check if early bird pricing is currently active"""
        now = datetime.utcnow()
        return (self.tanggal_mulai_early_bird <= now <= self.tanggal_akhir_early_bird)
    
    def get_participant_count(self):
        """Get total number of participants registered for this competition"""
        return self.registrations.filter_by(status='approved').count()
    
    def is_user_eligible(self, user):
        """Check if user is eligible for this competition"""
        if not user or not user.profile:
            return False
        
        # Check if profile is complete and verified
        if not user.is_profile_complete():
            return False
        
        # Check grade eligibility
        if not user.profile.is_grade_eligible(self.min_kelas, self.max_kelas):
            return False
        
        # Check registration deadline
        if datetime.utcnow() > self.deadline_registrasi:
            return False
        
        return True
    
    def get_early_bird_savings(self):
        """Calculate savings amount during early bird period"""
        return self.harga_reguler - self.harga_early_bird
    
    def get_early_bird_days_left(self):
        """Get number of days left for early bird pricing"""
        if not self.is_early_bird_active():
            return 0
        
        now = datetime.utcnow()
        if now < self.tanggal_mulai_early_bird:
            return 0
        
        days_left = (self.tanggal_akhir_early_bird - now).days
        return max(0, days_left)
    
    def is_registration_open(self):
        """Check if registration is still open"""
        return datetime.utcnow() <= self.deadline_registrasi
    
    def get_registration_days_left(self):
        """Get number of days left for registration"""
        if not self.is_registration_open():
            return 0
        
        days_left = (self.deadline_registrasi - datetime.utcnow()).days
        return max(0, days_left)
    
    def get_locked_price_at_registration(self, registration_date=None):
        """Get the price that should be locked at registration time"""
        if registration_date is None:
            registration_date = datetime.utcnow()
        
        # Check if registration date falls within early bird period
        if (self.tanggal_mulai_early_bird <= registration_date <= self.tanggal_akhir_early_bird):
            return self.harga_early_bird
        return self.harga_reguler
    
    def get_pricing_info(self):
        """Get comprehensive pricing information"""
        now = datetime.utcnow()
        
        pricing_info = {
            'current_price': self.get_current_price(),
            'early_bird_price': self.harga_early_bird,
            'regular_price': self.harga_reguler,
            'is_early_bird_active': self.is_early_bird_active(),
            'early_bird_savings': self.get_early_bird_savings(),
            'early_bird_days_left': self.get_early_bird_days_left(),
            'early_bird_start': self.tanggal_mulai_early_bird,
            'early_bird_end': self.tanggal_akhir_early_bird,
            'registration_deadline': self.deadline_registrasi,
            'registration_days_left': self.get_registration_days_left(),
            'is_registration_open': self.is_registration_open()
        }
        
        return pricing_info
    
    def validate_early_bird_dates(self):
        """Validate early bird date configuration"""
        errors = []
        
        if self.tanggal_mulai_early_bird >= self.tanggal_akhir_early_bird:
            errors.append("Tanggal mulai early bird harus sebelum tanggal akhir")
        
        if self.tanggal_akhir_early_bird >= self.deadline_registrasi:
            errors.append("Tanggal akhir early bird harus sebelum deadline registrasi")
        
        if self.deadline_registrasi >= self.tanggal_kompetisi:
            errors.append("Deadline registrasi harus sebelum tanggal kompetisi")
        
        if self.harga_early_bird >= self.harga_reguler:
            errors.append("Harga early bird harus lebih murah dari harga reguler")
        
        return errors
    
    def validate_team_size(self, member_count):
        """Validate if team size is within allowed range"""
        if self.kategori != 'team':
            return True
        
        if not self.min_anggota or not self.max_anggota:
            return True
        
        return self.min_anggota <= member_count <= self.max_anggota
    
    def get_competition_type_display(self):
        """Get human-readable competition type"""
        type_mapping = {
            'academic': 'Akademik',
            'creative': 'Kreatif', 
            'performance': 'Performa',
            'basketball': 'Basket',
            'esports': 'E-Sports'
        }
        return type_mapping.get(self.jenis, self.jenis.title())
    
    def get_category_display(self):
        """Get human-readable category"""
        return 'Individu' if self.kategori == 'individual' else 'Tim'


class CompetitionCategory(db.Model):
    """Competition category definitions and rules"""
    __tablename__ = 'competition_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_kategori = db.Column(db.String(50), unique=True, nullable=False)
    deskripsi = db.Column(db.Text)
    
    # Category type
    tipe_kompetisi = db.Column(db.String(20), nullable=False)  # 'individual' or 'team'
    
    # Submission requirements
    requires_file_upload = db.Column(db.Boolean, default=False)
    requires_google_drive = db.Column(db.Boolean, default=False)
    allowed_file_types = db.Column(db.String(200))  # Comma-separated file extensions
    max_file_size_mb = db.Column(db.Integer, default=10)
    
    # Team constraints (if applicable)
    min_team_size = db.Column(db.Integer)
    max_team_size = db.Column(db.Integer)
    
    # Display order
    display_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompetitionCategory {self.nama_kategori}>'
    
    def get_allowed_extensions(self):
        """Get list of allowed file extensions"""
        if not self.allowed_file_types:
            return []
        return [ext.strip() for ext in self.allowed_file_types.split(',')]
    
    def is_file_allowed(self, filename):
        """Check if file extension is allowed"""
        if not self.requires_file_upload:
            return True
        
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        allowed_extensions = self.get_allowed_extensions()
        
        return extension in allowed_extensions
    
    def get_submission_requirements(self):
        """Get submission requirements as a dictionary"""
        return {
            'file_upload': self.requires_file_upload,
            'google_drive': self.requires_google_drive,
            'allowed_types': self.get_allowed_extensions(),
            'max_size_mb': self.max_file_size_mb
        }
    
    @staticmethod
    def create_default_categories():
        """Create default competition categories"""
        categories = [
            {
                'nama_kategori': 'Math Olympiad',
                'deskripsi': 'Olimpiade Matematika untuk siswa SMP',
                'tipe_kompetisi': 'individual',
                'requires_file_upload': True,
                'allowed_file_types': 'pdf,doc,docx',
                'display_order': 1
            },
            {
                'nama_kategori': 'Science Olympiad',
                'deskripsi': 'Olimpiade Sains untuk siswa SMP',
                'tipe_kompetisi': 'individual',
                'requires_file_upload': True,
                'allowed_file_types': 'pdf,doc,docx',
                'display_order': 2
            },
            {
                'nama_kategori': 'Logic Olympiad',
                'deskripsi': 'Olimpiade Logika untuk siswa SMP',
                'tipe_kompetisi': 'individual',
                'requires_file_upload': True,
                'allowed_file_types': 'pdf,doc,docx',
                'display_order': 3
            },
            {
                'nama_kategori': 'Informatics Olympiad',
                'deskripsi': 'Olimpiade Informatika untuk siswa SMP',
                'tipe_kompetisi': 'individual',
                'requires_file_upload': True,
                'allowed_file_types': 'pdf,doc,docx,py,cpp,java',
                'display_order': 4
            },
            {
                'nama_kategori': 'Digital Poster',
                'deskripsi': 'Kompetisi poster digital kreatif',
                'tipe_kompetisi': 'individual',
                'requires_google_drive': True,
                'display_order': 5
            },
            {
                'nama_kategori': 'Scientific Writing',
                'deskripsi': 'Kompetisi karya tulis ilmiah',
                'tipe_kompetisi': 'individual',
                'requires_google_drive': True,
                'display_order': 6
            },
            {
                'nama_kategori': 'Speech',
                'deskripsi': 'Kompetisi pidato bahasa Inggris',
                'tipe_kompetisi': 'individual',
                'requires_google_drive': True,
                'display_order': 7
            },
            {
                'nama_kategori': 'Solo Vocal',
                'deskripsi': 'Kompetisi vokal solo',
                'tipe_kompetisi': 'individual',
                'requires_google_drive': True,
                'display_order': 8
            },
            {
                'nama_kategori': 'Basketball',
                'deskripsi': 'Kompetisi basket tim',
                'tipe_kompetisi': 'team',
                'min_team_size': 5,
                'max_team_size': 8,
                'display_order': 9
            },
            {
                'nama_kategori': 'E-Sports',
                'deskripsi': 'Kompetisi e-sports tim',
                'tipe_kompetisi': 'team',
                'min_team_size': 5,
                'max_team_size': 7,
                'display_order': 10
            }
        ]
        
        for cat_data in categories:
            existing = CompetitionCategory.query.filter_by(nama_kategori=cat_data['nama_kategori']).first()
            if not existing:
                category = CompetitionCategory(**cat_data)
                db.session.add(category)
        
        db.session.commit()