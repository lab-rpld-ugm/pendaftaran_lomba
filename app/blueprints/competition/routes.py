from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.blueprints.competition import bp
from app.models.competition import Competition
from app.models.registration import Registration, IndividualRegistration
from app.models.payment import Payment
from app.forms.registration import IndividualRegistrationForm
from app.utils.verification import profile_required, verification_required
from app.utils.file_handler import save_uploaded_file, get_upload_path
from datetime import datetime
import os

@bp.route('/')
def index():
    """Competition listing with filtering"""
    # Get filter parameters
    kategori_filter = request.args.get('kategori', '')
    jenis_filter = request.args.get('jenis', '')
    kelas_filter = request.args.get('kelas', type=int)
    
    # Base query
    query = Competition.query
    
    # Apply filters
    if kategori_filter:
        query = query.filter(Competition.kategori == kategori_filter)
    
    if jenis_filter:
        query = query.filter(Competition.jenis == jenis_filter)
    
    if kelas_filter and current_user.is_authenticated and current_user.profile:
        # Filter competitions where user's grade is eligible
        user_kelas = current_user.profile.kelas
        if user_kelas:
            query = query.filter(
                Competition.min_kelas <= user_kelas,
                Competition.max_kelas >= user_kelas
            )
    elif kelas_filter:
        # Filter by specific grade if user not logged in or no profile
        query = query.filter(
            Competition.min_kelas <= kelas_filter,
            Competition.max_kelas >= kelas_filter
        )
    
    # Order by competition date
    competitions = query.order_by(Competition.tanggal_kompetisi.asc()).all()
    
    # Get unique filter options for dropdowns
    all_competitions = Competition.query.all()
    available_categories = list(set(comp.kategori for comp in all_competitions))
    available_types = list(set(comp.jenis for comp in all_competitions))
    available_grades = list(range(7, 10))  # Grades 7, 8, 9
    
    return render_template('competition/index.html', 
                         competitions=competitions,
                         available_categories=available_categories,
                         available_types=available_types,
                         available_grades=available_grades,
                         current_filters={
                             'kategori': kategori_filter,
                             'jenis': jenis_filter,
                             'kelas': kelas_filter
                         })

@bp.route('/<int:id>')
def detail(id):
    """Competition detail"""
    competition = Competition.query.get_or_404(id)
    
    # Check user eligibility if logged in
    user_eligible = False
    eligibility_reason = ""
    
    if current_user.is_authenticated:
        user_eligible = competition.is_user_eligible(current_user)
        if not user_eligible:
            # Determine specific reason for ineligibility
            if not current_user.profile:
                eligibility_reason = "Profil belum dibuat"
            elif not current_user.is_profile_complete():
                eligibility_reason = "Profil belum lengkap"
            elif current_user.profile.kelas and not (competition.min_kelas <= current_user.profile.kelas <= competition.max_kelas):
                eligibility_reason = f"Kompetisi hanya untuk kelas {competition.min_kelas}-{competition.max_kelas}"
            elif not competition.is_registration_open():
                eligibility_reason = "Pendaftaran sudah ditutup"
            else:
                eligibility_reason = "Tidak memenuhi persyaratan"
    
    return render_template('competition/detail.html', 
                         competition=competition,
                         user_eligible=user_eligible,
                         eligibility_reason=eligibility_reason)

def calculate_locked_price(competition, registration_date=None):
    """Calculate and return the price that should be locked at registration time"""
    if registration_date is None:
        registration_date = datetime.utcnow()
    
    # Validate early bird dates
    validation_errors = competition.validate_early_bird_dates()
    if validation_errors:
        # If there are validation errors, use regular price as fallback
        return competition.harga_reguler
    
    # Get locked price based on registration date
    locked_price = competition.get_locked_price_at_registration(registration_date)
    
    return locked_price

def get_pricing_display_info(competition):
    """Get comprehensive pricing information for display"""
    pricing_info = competition.get_pricing_info()
    
    # Add display-specific information
    pricing_info.update({
        'savings_percentage': round((pricing_info['early_bird_savings'] / pricing_info['regular_price']) * 100, 1) if pricing_info['regular_price'] > 0 else 0,
        'current_price_formatted': f"Rp {pricing_info['current_price']:,}",
        'early_bird_price_formatted': f"Rp {pricing_info['early_bird_price']:,}",
        'regular_price_formatted': f"Rp {pricing_info['regular_price']:,}",
        'savings_formatted': f"Rp {pricing_info['early_bird_savings']:,}",
        'early_bird_end_formatted': pricing_info['early_bird_end'].strftime('%d %B %Y'),
        'registration_deadline_formatted': pricing_info['registration_deadline'].strftime('%d %B %Y'),
    })
    
    return pricing_info

@bp.route('/<int:id>/pricing-info')
def pricing_info(id):
    """Get real-time pricing information (AJAX endpoint)"""
    competition = Competition.query.get_or_404(id)
    pricing_info = get_pricing_display_info(competition)
    
    return {
        'success': True,
        'pricing': pricing_info,
        'locked_price': calculate_locked_price(competition),
        'locked_price_formatted': f"Rp {calculate_locked_price(competition):,}"
    }

@bp.route('/<int:id>/participant-count')
def participant_count(id):
    """Get real-time participant count (AJAX endpoint)"""
    competition = Competition.query.get_or_404(id)
    count = competition.get_participant_count()
    
    return {
        'success': True,
        'count': count,
        'competition_id': id
    }

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/uploads')
    return send_from_directory(upload_folder, filename)

@bp.route('/<int:id>/daftar', methods=['GET', 'POST'])
@login_required
@profile_required
def register(id):
    """Individual competition registration with form handling"""
    from app import db
    
    competition = Competition.query.get_or_404(id)
    
    # Only allow individual competitions for this route
    if competition.kategori != 'individual':
        flash('Route ini hanya untuk kompetisi individu.', 'error')
        return redirect(url_for('competition.detail', id=id))
    
    # Double-check eligibility
    if not competition.is_user_eligible(current_user):
        flash('Anda tidak memenuhi persyaratan untuk kompetisi ini.', 'error')
        return redirect(url_for('competition.detail', id=id))
    
    # Check if user is already registered for this competition
    existing_registration = Registration.query.filter_by(
        user_id=current_user.id,
        competition_id=competition.id
    ).first()
    
    if existing_registration:
        flash('Anda sudah terdaftar untuk kompetisi ini.', 'warning')
        return redirect(url_for('competition.detail', id=id))
    
    # Create form with competition context
    form = IndividualRegistrationForm(competition=competition)
    
    if form.validate_on_submit():
        try:
            # Validate registration eligibility
            is_eligible, reason = form.validate_registration_eligibility()
            if not is_eligible:
                flash(f'Pendaftaran tidak dapat diproses: {reason}', 'error')
                return redirect(url_for('competition.detail', id=id))
            
            # Calculate locked price
            locked_price = calculate_locked_price(competition)
            
            # Create individual registration
            registration = IndividualRegistration(
                user_id=current_user.id,
                competition_id=competition.id,
                harga_terkunci=locked_price,
                status='pending'
            )
            
            # Handle file submission for academic competitions
            if form.file_submission.data:
                try:
                    from app.utils.file_handler import save_academic_submission
                    filename = save_academic_submission(
                        form.file_submission.data,
                        current_user.id,
                        competition.id,
                        competition.jenis
                    )
                    registration.file_submission = filename
                except Exception as e:
                    flash(f'Gagal menyimpan file: {str(e)}', 'error')
                    return render_template('competition/register.html', 
                                         form=form, 
                                         competition=competition,
                                         pricing_info=get_pricing_display_info(competition))
            
            # Handle Google Drive link for creative/performance competitions
            if form.google_drive_link.data:
                registration.google_drive_link = form.google_drive_link.data.strip()
            
            # Save registration
            db.session.add(registration)
            db.session.commit()
            
            # Create payment record
            payment = Payment(
                registration_id=registration.id,
                jumlah=locked_price,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            flash(f'Pendaftaran berhasil! Harga terkunci: Rp {locked_price:,}. Silakan upload bukti pembayaran dalam 24 jam.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('Terjadi kesalahan saat memproses pendaftaran. Silakan coba lagi.', 'error')
    
    # GET request or form validation failed
    pricing_info = get_pricing_display_info(competition)
    
    return render_template('competition/register.html', 
                         form=form, 
                         competition=competition,
                         pricing_info=pricing_info)