from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User


class RegistrationForm(FlaskForm):
    """Form untuk registrasi pengguna baru"""
    email = StringField('Email', validators=[
        DataRequired(message='Email wajib diisi'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Kata Sandi', validators=[
        DataRequired(message='Kata sandi wajib diisi'),
        Length(min=6, message='Kata sandi minimal 6 karakter')
    ])
    password2 = PasswordField('Konfirmasi Kata Sandi', validators=[
        DataRequired(message='Konfirmasi kata sandi wajib diisi'),
        EqualTo('password', message='Kata sandi tidak cocok')
    ])
    submit = SubmitField('Daftar')
    
    def validate_email(self, email):
        """Validasi email uniqueness"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')


class LoginForm(FlaskForm):
    """Form untuk login pengguna"""
    email = StringField('Email', validators=[
        DataRequired(message='Email wajib diisi'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Kata Sandi', validators=[
        DataRequired(message='Kata sandi wajib diisi')
    ])
    remember_me = BooleanField('Ingat Saya')
    submit = SubmitField('Masuk')