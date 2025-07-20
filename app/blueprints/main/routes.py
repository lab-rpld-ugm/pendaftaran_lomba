from flask import render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.blueprints.main import bp
from app.forms.profile import ProfileForm
from app.models.user import UserProfile
from app.utils.file_handler import FileHandler
from app.utils.verification import ProfileVerificationHelper, check_competition_eligibility
import os

@bp.route('/')
def index():
    """Homepage"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('main/dashboard.html')

@bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    """User profile management"""
    # Create or get existing profile
    if not current_user.profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    else:
        profile = current_user.profile
    
    form = ProfileForm(current_user=current_user)
    
    if form.validate_on_submit():
        try:
            # Update profile fields
            profile.nama_lengkap = form.nama_lengkap.data
            profile.sekolah = form.sekolah.data
            profile.kelas = form.kelas.data
            profile.nisn = form.nisn.data
            profile.whatsapp = form.whatsapp.data
            profile.instagram = form.instagram.data.lstrip('@')
            
            # Handle file uploads
            upload_errors = []
            
            # Handle foto_kartu_pelajar upload
            if form.foto_kartu_pelajar.data:
                success, result = FileHandler.save_uploaded_file(
                    form.foto_kartu_pelajar.data,
                    'profile_photos',
                    f'kartu_{current_user.id}',
                    'profile_photo'
                )
                if success:
                    # Delete old file if exists
                    if profile.foto_kartu_pelajar:
                        FileHandler.delete_file(profile.foto_kartu_pelajar, 'profile_photos')
                    profile.foto_kartu_pelajar = result
                else:
                    upload_errors.append(f'Foto kartu pelajar: {result}')
            
            # Handle screenshot_twibbon upload
            if form.screenshot_twibbon.data:
                success, result = FileHandler.save_uploaded_file(
                    form.screenshot_twibbon.data,
                    'twibbon_screenshots',
                    f'twibbon_{current_user.id}',
                    'twibbon'
                )
                if success:
                    # Delete old file if exists
                    if profile.screenshot_twibbon:
                        FileHandler.delete_file(profile.screenshot_twibbon, 'twibbon_screenshots')
                    profile.screenshot_twibbon = result
                else:
                    upload_errors.append(f'Screenshot twibbon: {result}')
            
            if upload_errors:
                for error in upload_errors:
                    flash(error, 'error')
                return render_template('main/profil.html', form=form, profile=profile)
            
            # Calculate completion percentage
            completion_percentage = profile.calculate_completion_percentage()
            
            # Save to database
            db.session.commit()
            
            flash(f'Profil berhasil disimpan! Kelengkapan: {completion_percentage}%', 'success')
            
            # Redirect to prevent form resubmission
            return redirect(url_for('main.profil'))
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan profil. Silakan coba lagi.', 'error')
            return render_template('main/profil.html', form=form, profile=profile)
    
    # Pre-populate form with existing data
    if request.method == 'GET' and profile:
        form.nama_lengkap.data = profile.nama_lengkap
        form.sekolah.data = profile.sekolah
        form.kelas.data = profile.kelas
        form.nisn.data = profile.nisn
        form.whatsapp.data = profile.whatsapp
        form.instagram.data = profile.instagram
    
    return render_template('main/profil.html', form=form, profile=profile)

@bp.route('/uploads/<path:subfolder>/<path:filename>')
def uploaded_file(subfolder, filename):
    """Serve uploaded files"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(upload_folder, subfolder), filename)