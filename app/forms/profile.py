from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, ValidationError, Optional
from werkzeug.utils import secure_filename
import os


class ProfileForm(FlaskForm):
    """Form untuk manajemen profil pengguna lengkap"""
    
    # Personal information fields
    nama_lengkap = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama lengkap wajib diisi'),
        Length(min=2, max=100, message='Nama lengkap harus antara 2-100 karakter')
    ])
    
    sekolah = StringField('Sekolah', validators=[
        DataRequired(message='Nama sekolah wajib diisi'),
        Length(min=2, max=100, message='Nama sekolah harus antara 2-100 karakter')
    ])
    
    # FIXED: Custom coerce function that handles empty strings
    def _coerce_kelas(value):
        """Custom coerce function for kelas field that handles empty strings"""
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    kelas = SelectField('Kelas', 
        choices=[
            ('', 'Pilih Kelas'),
            (7, 'Kelas 7'),
            (8, 'Kelas 8'), 
            (9, 'Kelas 9')
        ],
        coerce=_coerce_kelas,  # Use custom coerce function
        validators=[
            DataRequired(message='Kelas wajib dipilih'),
            NumberRange(min=7, max=9, message='Kelas harus antara 7-9')
        ]
    )
    
    nisn = StringField('NISN (Nomor Induk Siswa Nasional)', validators=[
        DataRequired(message='NISN wajib diisi'),
        Length(min=10, max=10, message='NISN harus 10 digit'),
        Regexp(r'^\d{10}$', message='NISN harus berupa 10 digit angka')
    ])
    
    # Contact information fields
    whatsapp = StringField('Nomor WhatsApp', validators=[
        DataRequired(message='Nomor WhatsApp wajib diisi'),
        Length(min=10, max=20, message='Nomor WhatsApp harus antara 10-20 karakter'),
        Regexp(r'^[\d\+\-\s\(\)]+$', message='Format nomor WhatsApp tidak valid')
    ])
    
    instagram = StringField('Username Instagram', validators=[
        DataRequired(message='Username Instagram wajib diisi'),
        Length(min=1, max=50, message='Username Instagram maksimal 50 karakter'),
        Regexp(r'^[a-zA-Z0-9._]+$', message='Username Instagram hanya boleh mengandung huruf, angka, titik, dan underscore')
    ])
    
    # Removed Twitter field
    
    # File upload fields with secure validation
    foto_kartu_pelajar = FileField('Foto Kartu Pelajar', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 
                   message='File harus berformat JPG, JPEG, PNG, atau PDF'),
    ])
    
    screenshot_twibbon = FileField('Screenshot Twibbon', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 
                   message='Screenshot harus berformat JPG, JPEG, atau PNG'),
    ])
    
    submit = SubmitField('Simpan Profil')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with current user data if editing"""
        self.current_user = kwargs.pop('current_user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
    
    def validate_kelas(self, kelas):
        """Custom validation for kelas field"""
        if kelas.data is None or kelas.data == '':
            raise ValidationError('Kelas wajib dipilih')
        if not isinstance(kelas.data, int) or kelas.data not in [7, 8, 9]:
            raise ValidationError('Kelas harus antara 7-9')
    
    def validate_nisn(self, nisn):
        """Validate NISN uniqueness across all users"""
        from app.models.user import UserProfile
        
        # Skip validation if this is the current user's existing NISN
        if self.current_user and self.current_user.profile:
            if self.current_user.profile.nisn == nisn.data:
                return
        
        # Check if NISN already exists
        existing_profile = UserProfile.query.filter_by(nisn=nisn.data).first()
        if existing_profile:
            raise ValidationError('NISN sudah terdaftar. Silakan periksa kembali.')
    
    def validate_instagram(self, instagram):
        """Validate Instagram username format and uniqueness"""
        from app.models.user import UserProfile
        
        # Remove @ symbol if present
        username = instagram.data.lstrip('@')
        instagram.data = username
        
        # Skip validation if this is the current user's existing Instagram
        if self.current_user and self.current_user.profile:
            if self.current_user.profile.instagram == username:
                return
        
        # Check uniqueness
        existing_profile = UserProfile.query.filter_by(instagram=username).first()
        if existing_profile:
            raise ValidationError('Username Instagram sudah digunakan.')
    
    # Removed validate_twitter
    
    def validate_whatsapp(self, whatsapp):
        """Validate WhatsApp number format"""
        # Clean the number (remove spaces, dashes, parentheses)
        cleaned_number = ''.join(filter(str.isdigit, whatsapp.data.replace('+', '')))
        
        # Indonesian phone number validation
        if not (cleaned_number.startswith('62') or cleaned_number.startswith('08')):
            if len(cleaned_number) >= 9:  # Allow other international formats
                return
            raise ValidationError('Nomor WhatsApp harus dimulai dengan +62, 62, atau 08')
        
        # Check minimum length for Indonesian numbers
        if cleaned_number.startswith('62') and len(cleaned_number) < 12:
            raise ValidationError('Nomor WhatsApp tidak valid (terlalu pendek)')
        elif cleaned_number.startswith('08') and len(cleaned_number) < 10:
            raise ValidationError('Nomor WhatsApp tidak valid (terlalu pendek)')
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """Check if file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def get_secure_filename(filename, prefix=''):
        """Get secure filename with optional prefix"""
        if not filename:
            return None
        
        # Get secure filename
        secure_name = secure_filename(filename)
        
        # Add prefix if provided
        if prefix:
            name, ext = os.path.splitext(secure_name)
            secure_name = f"{prefix}_{name}{ext}"
        
        return secure_name
    
    def get_file_upload_errors(self):
        """Get specific file upload validation errors"""
        errors = []
        
        # Check foto_kartu_pelajar
        if self.foto_kartu_pelajar.data:
            if not self.allowed_file(self.foto_kartu_pelajar.data.filename, 
                                   ['jpg', 'jpeg', 'png', 'pdf']):
                errors.append('Foto kartu pelajar harus berformat JPG, JPEG, PNG, atau PDF')
        
        # Check screenshot_twibbon
        if self.screenshot_twibbon.data:
            if not self.allowed_file(self.screenshot_twibbon.data.filename,
                                   ['jpg', 'jpeg', 'png']):
                errors.append('Screenshot twibbon harus berformat JPG, JPEG, atau PNG')
        
        return errors