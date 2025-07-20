from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


def profile_required(f):
    """
    Decorator to require complete profile before accessing certain routes
    Redirects to profile page if profile is not 100% complete
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.masuk'))
        
        # Allow admins to bypass profile completion
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            return f(*args, **kwargs)
        
        if not current_user.is_profile_complete():
            flash('Anda harus melengkapi profil hingga 100% sebelum dapat mengakses fitur ini.', 'warning')
            return redirect(url_for('main.profil'))
        
        return f(*args, **kwargs)
    return decorated_function


def verification_required(f):
    """
    Decorator to require verified profile before accessing certain routes
    Redirects to profile page if profile is not verified by admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.masuk'))
        
        # Allow admins to bypass verification
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            return f(*args, **kwargs)
        
        if not current_user.profile or not current_user.profile.is_verified:
            if not current_user.is_profile_complete():
                flash('Anda harus melengkapi profil hingga 100% dan menunggu verifikasi admin sebelum dapat mengakses fitur ini.', 'warning')
            else:
                flash('Profil Anda sedang dalam proses verifikasi admin. Silakan tunggu konfirmasi.', 'info')
            return redirect(url_for('main.profil'))
        
        return f(*args, **kwargs)
    return decorated_function


class ProfileVerificationHelper:
    """Helper class for profile verification utilities"""
    
    @staticmethod
    def can_register_competition(user):
        """
        Check if user can register for competitions
        Returns tuple: (can_register: bool, reason: str)
        """
        if not user.is_authenticated:
            return False, 'Anda harus login terlebih dahulu'
        
        if not user.profile:
            return False, 'Anda harus membuat profil terlebih dahulu'
        
        if not user.is_profile_complete():
            completion = user.get_verification_progress()
            return False, f'Profil belum lengkap ({completion}%). Lengkapi profil hingga 100%'
        
        if not user.profile.is_verified:
            return False, 'Profil sedang dalam proses verifikasi admin'
        
        return True, 'Dapat mendaftar kompetisi'
    
    @staticmethod
    def get_profile_status_info(user):
        """
        Get comprehensive profile status information
        Returns dict with status details
        """
        if not user.is_authenticated:
            return {
                'status': 'not_logged_in',
                'message': 'Belum login',
                'can_register': False,
                'completion_percentage': 0
            }
        
        if not user.profile:
            return {
                'status': 'no_profile',
                'message': 'Belum membuat profil',
                'can_register': False,
                'completion_percentage': 0
            }
        
        completion = user.get_verification_progress()
        
        if completion < 100:
            return {
                'status': 'incomplete',
                'message': f'Profil belum lengkap ({completion}%)',
                'can_register': False,
                'completion_percentage': completion,
                'missing_fields': user.profile.get_missing_fields()
            }
        
        if not user.profile.is_verified:
            return {
                'status': 'pending_verification',
                'message': 'Menunggu verifikasi admin',
                'can_register': False,
                'completion_percentage': completion
            }
        
        return {
            'status': 'verified',
            'message': 'Profil terverifikasi',
            'can_register': True,
            'completion_percentage': completion
        }
    
    @staticmethod
    def get_verification_badge_class(user):
        """Get Bootstrap badge class based on verification status"""
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        status = status_info['status']
        
        badge_classes = {
            'not_logged_in': 'bg-secondary',
            'no_profile': 'bg-danger',
            'incomplete': 'bg-warning text-dark',
            'pending_verification': 'bg-info',
            'verified': 'bg-success'
        }
        
        return badge_classes.get(status, 'bg-secondary')
    
    @staticmethod
    def get_verification_icon(user):
        """Get Font Awesome icon based on verification status"""
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        status = status_info['status']
        
        icons = {
            'not_logged_in': 'fas fa-user-slash',
            'no_profile': 'fas fa-user-plus',
            'incomplete': 'fas fa-user-edit',
            'pending_verification': 'fas fa-clock',
            'verified': 'fas fa-user-check'
        }
        
        return icons.get(status, 'fas fa-user')
    
    @staticmethod
    def get_next_action_message(user):
        """Get message about what user should do next"""
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        status = status_info['status']
        
        messages = {
            'not_logged_in': 'Silakan login untuk melanjutkan',
            'no_profile': 'Lengkapi profil Anda untuk dapat mendaftar kompetisi',
            'incomplete': f'Lengkapi {len(status_info.get("missing_fields", []))} field yang tersisa',
            'pending_verification': 'Tunggu verifikasi admin (biasanya 1-2 hari kerja)',
            'verified': 'Anda dapat mendaftar kompetisi'
        }
        
        return messages.get(status, 'Status tidak diketahui')


def check_competition_eligibility(user, competition=None):
    """
    Check if user is eligible to register for a specific competition
    Returns tuple: (eligible: bool, reason: str)
    """
    # First check basic profile requirements
    can_register, reason = ProfileVerificationHelper.can_register_competition(user)
    if not can_register:
        return False, reason
    
    # If competition is specified, check competition-specific requirements
    if competition:
        # Check grade eligibility
        if user.profile.kelas:
            min_grade = getattr(competition, 'min_kelas', 7)
            max_grade = getattr(competition, 'max_kelas', 9)
            
            if not (min_grade <= user.profile.kelas <= max_grade):
                return False, f'Kompetisi ini hanya untuk kelas {min_grade}-{max_grade}'
        
        # Check if registration is still open
        from datetime import datetime
        if hasattr(competition, 'deadline_registrasi'):
            if competition.deadline_registrasi and datetime.now() > competition.deadline_registrasi:
                return False, 'Pendaftaran kompetisi sudah ditutup'
    
    return True, 'Memenuhi syarat untuk mendaftar'