from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, HiddenField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, URL, Optional, ValidationError
from flask_login import current_user
from datetime import datetime, timedelta
import re


class IndividualRegistrationForm(FlaskForm):
    """Form untuk registrasi kompetisi individu"""
    
    # Hidden fields for competition data
    competition_id = HiddenField('Competition ID', validators=[DataRequired()])
    locked_price = HiddenField('Locked Price', validators=[DataRequired()])
    
    # File submission for academic competitions (Math, Science, Logic, Informatics)
    file_submission = FileField('Upload File Karya', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'py', 'cpp', 'java', 'txt'], 
                   message='File harus berformat PDF, DOC, DOCX, PY, CPP, JAVA, atau TXT')
    ])
    
    # Google Drive link for creative/performance competitions
    google_drive_link = StringField('Link Google Drive', validators=[
        Optional(),
        Length(max=500, message='Link terlalu panjang (maksimal 500 karakter)'),
    ])
    
    # Additional notes (optional)
    catatan = TextAreaField('Catatan Tambahan (Opsional)', validators=[
        Optional(),
        Length(max=500, message='Catatan maksimal 500 karakter')
    ])
    
    submit = SubmitField('Daftar Kompetisi')
    
    def __init__(self, competition=None, *args, **kwargs):
        """Initialize form with competition context"""
        super(IndividualRegistrationForm, self).__init__(*args, **kwargs)
        self.competition = competition
        
        # Set competition_id if provided
        if competition:
            self.competition_id.data = competition.id
            self.locked_price.data = competition.get_current_price()
            
            # Adjust form fields based on competition type
            self._adjust_fields_for_competition_type()
    
    def _adjust_fields_for_competition_type(self):
        """Adjust form fields based on competition type"""
        if not self.competition:
            return
        
        competition_type = self.competition.jenis.lower()
        
        # Academic competitions require file upload
        if competition_type in ['math', 'science', 'logic', 'informatics']:
            self.file_submission.validators.append(
                DataRequired(message='File karya wajib diupload untuk kompetisi akademik')
            )
            # Remove Google Drive requirement
            self.google_drive_link.render_kw = {'style': 'display: none;'}
            
        # Creative and Performance competitions require Google Drive link
        elif competition_type in ['creative', 'performance']:
            self.google_drive_link.validators.append(
                DataRequired(message='Link Google Drive wajib diisi untuk kompetisi kreatif/performa')
            )
            # Remove file upload requirement
            self.file_submission.render_kw = {'style': 'display: none;'}
    
    def validate_competition_id(self, competition_id):
        """Validate competition exists and is available for registration"""
        from app.models.competition import Competition
        
        competition = Competition.query.get(competition_id.data)
        if not competition:
            raise ValidationError('Kompetisi tidak ditemukan.')
        
        # Check if registration is still open
        if not competition.is_registration_open():
            raise ValidationError('Pendaftaran untuk kompetisi ini sudah ditutup.')
        
        # Check if user is eligible
        if not competition.is_user_eligible(current_user):
            raise ValidationError('Anda tidak memenuhi persyaratan untuk kompetisi ini.')
    
    def validate_locked_price(self, locked_price):
        """Validate locked price matches current competition price"""
        from app.models.competition import Competition
        
        if not self.competition_id.data:
            return
        
        competition = Competition.query.get(self.competition_id.data)
        if not competition:
            return
        
        current_price = competition.get_current_price()
        submitted_price = int(locked_price.data)
        
        # Allow small difference for timing issues (within 1 rupiah)
        if abs(submitted_price - current_price) > 1:
            raise ValidationError('Harga telah berubah. Silakan refresh halaman dan coba lagi.')
    
    def validate_google_drive_link(self, google_drive_link):
        """Validate that a link is provided and looks like a URL (very basic check)."""
        if not google_drive_link.data:
            raise ValidationError('Silakan masukkan link karya atau dokumen yang dapat diakses.')
        link = google_drive_link.data.strip()
        # Very basic check: must contain at least one dot and not be just text
        if '.' not in link or ' ' in link:
            raise ValidationError('Link tidak valid. Pastikan Anda memasukkan link yang benar.')
    
    def validate_file_submission(self, file_submission):
        """Validate file submission based on competition requirements"""
        if not file_submission.data:
            return
        
        if not self.competition:
            return
        
        # Use enhanced academic file validation
        from app.utils.file_handler import validate_academic_file
        
        competition_type = self.competition.jenis.lower()
        is_valid, error_message = validate_academic_file(file_submission.data, competition_type)
        
        if not is_valid:
            raise ValidationError(error_message)
    
    def validate_registration_eligibility(self):
        """Validate overall registration eligibility"""
        if not current_user.is_authenticated:
            return False, "User harus login"
        
        if not current_user.is_profile_complete():
            return False, "Profil harus lengkap dan terverifikasi"
        
        # Check if user already registered for this competition
        from app.models.registration import Registration
        
        existing_registration = Registration.query.filter_by(
            user_id=current_user.id,
            competition_id=self.competition_id.data
        ).first()
        
        if existing_registration:
            return False, "Anda sudah terdaftar untuk kompetisi ini"
        
        return True, "Eligible"
    
    def get_submission_type(self):
        """Get the type of submission required for this competition"""
        if not self.competition:
            return 'unknown'
        
        competition_type = self.competition.jenis.lower()
        
        if competition_type in ['math', 'science', 'logic', 'informatics']:
            return 'file_upload'
        elif competition_type in ['creative', 'performance']:
            return 'google_drive'
        else:
            return 'unknown'
    
    def prepare_submission_data(self):
        """Prepare submission data for saving"""
        submission_data = {
            'file_submission': None,
            'google_drive_link': None
        }
        
        submission_type = self.get_submission_type()
        
        if submission_type == 'file_upload' and self.file_submission.data:
            # File will be handled by the route
            submission_data['has_file'] = True
            submission_data['filename'] = self.file_submission.data.filename
        elif submission_type == 'google_drive' and self.google_drive_link.data:
            submission_data['google_drive_link'] = self.google_drive_link.data.strip()
        
        return submission_data
    
    @staticmethod
    def get_allowed_file_extensions(competition_type):
        """Get allowed file extensions for competition type"""
        extensions_map = {
            'math': ['pdf', 'doc', 'docx'],
            'science': ['pdf', 'doc', 'docx'],
            'logic': ['pdf', 'doc', 'docx'],
            'informatics': ['pdf', 'doc', 'docx', 'py', 'cpp', 'java', 'txt', 'zip'],
            'creative': [],  # Uses Google Drive
            'performance': []  # Uses Google Drive
        }
        
        return extensions_map.get(competition_type.lower(), ['pdf', 'doc', 'docx'])
    
    @staticmethod
    def requires_file_upload(competition_type):
        """Check if competition type requires file upload"""
        return competition_type.lower() in ['math', 'science', 'logic', 'informatics']
    
    @staticmethod
    def requires_google_drive(competition_type):
        """Check if competition type requires Google Drive link"""
        return competition_type.lower() in ['creative', 'performance']