from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.competition import Competition
from app.models.registration import Team
from app.models.user import User


class CreateTeamForm(FlaskForm):
    """Form for creating a new team"""
    nama_tim = StringField('Nama Tim', validators=[
        DataRequired(message='Nama tim harus diisi'),
        Length(min=3, max=100, message='Nama tim harus antara 3-100 karakter')
    ])
    
    competition_id = HiddenField('Competition ID', validators=[DataRequired()])
    
    submit = SubmitField('Buat Tim')
    
    def __init__(self, competition=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.competition = competition
        if competition:
            self.competition_id.data = competition.id
    
    def validate_nama_tim(self, field):
        """Validate team name uniqueness per competition"""
        if self.competition:
            existing_team = Team.query.filter_by(
                nama_tim=field.data,
                competition_id=self.competition.id
            ).first()
            
            if existing_team:
                raise ValidationError('Nama tim sudah digunakan untuk kompetisi ini')
    
    def validate_competition_id(self, field):
        """Validate competition exists and is team-based"""
        competition = Competition.query.get(field.data)
        if not competition:
            raise ValidationError('Kompetisi tidak ditemukan')
        
        if competition.kategori != 'team':
            raise ValidationError('Kompetisi ini bukan untuk tim')
        
        if not competition.is_registration_open():
            raise ValidationError('Pendaftaran kompetisi sudah ditutup')


class AddMemberForm(FlaskForm):
    """Form for adding members to a team"""
    email = StringField('Email Anggota', validators=[
        DataRequired(message='Email harus diisi')
    ])
    
    posisi = SelectField('Posisi', choices=[
        ('Player', 'Pemain'),
        ('Reserve', 'Cadangan')
    ], default='Player')
    
    submit = SubmitField('Tambah Anggota')
    
    def __init__(self, team=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = team
    
    def validate_email(self, field):
        """Validate user exists and is eligible"""
        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError('User dengan email ini tidak ditemukan')
        
        if not user.is_profile_complete():
            raise ValidationError('User harus melengkapi profil terlebih dahulu')
        
        if self.team:
            # Check if user is already in this team
            from app.models.registration import TeamMember
            existing_member = TeamMember.query.filter_by(
                team_id=self.team.id,
                user_id=user.id
            ).first()
            
            if existing_member:
                raise ValidationError('User sudah menjadi anggota tim ini')
            
            # Check if user is already in another team for same competition
            existing_team_member = TeamMember.query.join(Team).filter(
                Team.competition_id == self.team.competition_id,
                TeamMember.user_id == user.id
            ).first()
            
            if existing_team_member:
                raise ValidationError('User sudah terdaftar di tim lain untuk kompetisi ini')
            
            # Check school consistency
            if self.team.members:
                captain = self.team.get_captain()
                if captain.profile and captain.profile.sekolah:
                    if user.profile.sekolah != captain.profile.sekolah:
                        raise ValidationError('Semua anggota tim harus dari sekolah yang sama')
        
        self.user = user


class TeamRegistrationForm(FlaskForm):
    """Form for registering a complete team for competition"""
    submit = SubmitField('Daftar Tim ke Kompetisi')
    
    def __init__(self, team=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = team
    
    def validate(self):
        """Validate team is complete and eligible"""
        if not super().validate():
            return False
        
        if not self.team:
            return False
        
        # Check if team is complete
        if not self.team.is_complete():
            self.submit.errors.append('Tim belum memenuhi persyaratan minimum')
            return False
        
        # Check competition eligibility
        from app.models.competition import Competition
        competition = Competition.query.get(self.team.competition_id)
        if not competition:
            self.submit.errors.append('Kompetisi tidak ditemukan')
            return False
        
        if not competition.is_registration_open():
            self.submit.errors.append('Pendaftaran kompetisi sudah ditutup')
            return False
        
        return True