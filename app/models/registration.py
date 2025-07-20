from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from app import db


class Registration(db.Model):
    """Base registration model for competitions"""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)  # For team registrations
    
    # Registration status
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected, cancelled
    
    # Pricing information (locked at registration time)
    harga_terkunci = db.Column(db.Integer, nullable=False)  # Price locked at registration
    
    # Submission information
    file_submission = db.Column(db.String(200))  # For academic competitions
    google_drive_link = db.Column(db.String(500))  # For creative/performance competitions
    
    # Timestamps
    tanggal_registrasi = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_approval = db.Column(db.DateTime)
    
    # Relationships
    payment = db.relationship('Payment', backref='registration', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Registration {self.id}: User {self.user_id} -> Competition {self.competition_id}>'
    
    def get_status_display(self):
        """Get human-readable status"""
        status_mapping = {
            'pending': 'Menunggu Persetujuan',
            'approved': 'Disetujui',
            'rejected': 'Ditolak',
            'cancelled': 'Dibatalkan'
        }
        return status_mapping.get(self.status, self.status.title())
    
    def can_submit_files(self):
        """Check if user can still submit files"""
        if self.status != 'pending':
            return False
        
        # Check if within submission deadline (24 hours after registration)
        deadline = self.tanggal_registrasi + timedelta(hours=24)
        return datetime.utcnow() <= deadline
    
    def get_submission_deadline(self):
        """Get submission deadline (24 hours after registration)"""
        return self.tanggal_registrasi + timedelta(hours=24)
    
    def is_submission_overdue(self):
        """Check if submission is overdue"""
        return datetime.utcnow() > self.get_submission_deadline()
    
    def approve_registration(self, admin_user_id=None):
        """Approve the registration"""
        self.status = 'approved'
        self.tanggal_approval = datetime.utcnow()
        db.session.commit()
    
    def reject_registration(self, admin_user_id=None):
        """Reject the registration"""
        self.status = 'rejected'
        db.session.commit()
    
    def get_type(self):
        """Get registration type (individual or team)"""
        return 'team' if self.team_id else 'individual'


class IndividualRegistration(Registration):
    """Individual competition registration"""
    __mapper_args__ = {
        'polymorphic_identity': 'individual'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure team_id is None for individual registrations
        self.team_id = None


class TeamRegistration(Registration):
    """Team competition registration"""
    __mapper_args__ = {
        'polymorphic_identity': 'team'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # team_id will be set when creating team registration


class Team(db.Model):
    """Team model for team-based competitions"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_tim = db.Column(db.String(100), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    captain_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', cascade='all, delete-orphan')
    registration = db.relationship('Registration', backref='team', uselist=False)
    
    # Unique constraint: team name must be unique per competition
    __table_args__ = (db.UniqueConstraint('nama_tim', 'competition_id', name='unique_team_name_per_competition'),)
    
    def __repr__(self):
        return f'<Team {self.nama_tim}>'
    
    def add_member(self, user, position='Player'):
        """Add a member to the team"""
        # Check if user is already a member
        existing_member = TeamMember.query.filter_by(team_id=self.id, user_id=user.id).first()
        if existing_member:
            return False, "User sudah menjadi anggota tim ini"
        
        # Check if user is already in another team for the same competition
        existing_team_member = db.session.query(TeamMember).join(Team).filter(
            Team.competition_id == self.competition_id,
            TeamMember.user_id == user.id
        ).first()
        
        if existing_team_member:
            return False, "User sudah terdaftar di tim lain untuk kompetisi ini"
        
        # Check team size limits
        competition = db.session.get(Competition, self.competition_id)
        current_size = len(self.members)
        
        if competition.max_anggota and current_size >= competition.max_anggota:
            return False, f"Tim sudah mencapai batas maksimal {competition.max_anggota} anggota"
        
        # Add member
        member = TeamMember(
            team_id=self.id,
            user_id=user.id,
            posisi=position
        )
        
        db.session.add(member)
        db.session.commit()
        
        return True, "Anggota berhasil ditambahkan"
    
    def remove_member(self, user_id):
        """Remove a member from the team"""
        # Cannot remove captain
        if user_id == self.captain_id:
            return False, "Captain tidak dapat dihapus dari tim"
        
        member = TeamMember.query.filter_by(team_id=self.id, user_id=user_id).first()
        if not member:
            return False, "User bukan anggota tim ini"
        
        db.session.delete(member)
        db.session.commit()
        
        return True, "Anggota berhasil dihapus"
    
    def validate_school_consistency(self):
        """Validate that all team members are from the same school"""
        if not self.members:
            return True, "Tim belum memiliki anggota"
        
        schools = set()
        for member in self.members:
            if member.user.profile and member.user.profile.sekolah:
                schools.add(member.user.profile.sekolah)
        
        if len(schools) > 1:
            return False, "Semua anggota tim harus dari sekolah yang sama"
        
        return True, "Konsistensi sekolah valid"
    
    def calculate_total_cost(self):
        """Calculate total cost for the team"""
        from app.models.competition import Competition
        competition = Competition.query.get(self.competition_id)
        if not competition:
            return 0
        
        member_count = len(self.members)
        price_per_person = competition.get_current_price()
        
        return member_count * price_per_person
    
    def is_complete(self):
        """Check if team meets minimum requirements"""
        from app.models.competition import Competition
        competition = Competition.query.get(self.competition_id)
        if not competition:
            return False
        
        current_size = len(self.members)
        
        # Check minimum size
        if competition.min_anggota and current_size < competition.min_anggota:
            return False
        
        # Check that all members are verified
        for member in self.members:
            if not member.user.is_profile_complete():
                return False
        
        # Check school consistency
        is_valid, _ = self.validate_school_consistency()
        if not is_valid:
            return False
        
        return True
    
    def get_captain(self):
        """Get team captain user object"""
        from app.models.user import User
        return User.query.get(self.captain_id)
    
    def get_member_count(self):
        """Get current number of team members"""
        return len(self.members)


class TeamMember(db.Model):
    """Team member model"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    posisi = db.Column(db.String(20), default='Player')  # Captain, Player, Reserve
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: user can only be in one position per team
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id', name='unique_user_per_team'),)
    
    def __repr__(self):
        return f'<TeamMember {self.user_id} in Team {self.team_id}>'
    
    def get_position_display(self):
        """Get human-readable position"""
        position_mapping = {
            'Captain': 'Kapten',
            'Player': 'Pemain',
            'Reserve': 'Cadangan'
        }
        return position_mapping.get(self.posisi, self.posisi)