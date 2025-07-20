from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.blueprints.payment import bp
from app.models.payment import Payment
from app.models.registration import Registration
from app.forms.payment import PaymentUploadForm, PaymentEditForm
from app.utils.verification import profile_required
from app.utils.file_handler import save_payment_proof, get_upload_path
from datetime import datetime
from app import db
import os


@bp.route('/<int:id>/upload', methods=['GET', 'POST'])
@login_required
@profile_required
def upload_proof(id):
    """Upload payment proof"""
    payment = Payment.query.get_or_404(id)
    
    # Check if user owns this payment
    if payment.registration.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke pembayaran ini.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if payment is still pending
    if payment.status != 'pending':
        flash('Pembayaran ini sudah diproses.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # Check if proof already uploaded
    if payment.bukti_pembayaran:
        flash('Bukti pembayaran sudah diupload.', 'info')
        return redirect(url_for('payment.view_proof', id=id))
    
    # Check if within deadline
    if payment.is_upload_deadline_passed():
        flash('Batas waktu upload bukti pembayaran sudah terlewat.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = PaymentUploadForm(payment=payment)
    
    if form.validate_on_submit():
        try:
            # Save payment proof file
            filename = save_payment_proof(
                form.bukti_pembayaran.data,
                payment.registration.user_id,
                payment.registration.competition_id,
                payment.id
            )
            
            # Update payment record
            payment.bukti_pembayaran = filename
            payment.catatan_user = form.catatan.data
            payment.tanggal_upload = datetime.utcnow()
            
            db.session.commit()
            
            flash('Bukti pembayaran berhasil diupload! Menunggu verifikasi admin.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Payment upload error: {str(e)}')
            flash('Terjadi kesalahan saat mengupload bukti pembayaran.', 'error')
    
    return render_template('payment/upload.html', 
                         form=form, 
                         payment=payment)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@profile_required
def edit_proof(id):
    """Edit payment proof (if allowed)"""
    payment = Payment.query.get_or_404(id)
    
    # Check if user owns this payment
    if payment.registration.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke pembayaran ini.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if payment can be modified
    if not payment.can_be_modified():
        flash('Pembayaran ini tidak dapat diubah.', 'warning')
        return redirect(url_for('payment.view_proof', id=id))
    
    form = PaymentEditForm(payment=payment)
    
    if form.validate_on_submit():
        try:
            # Delete old file if exists
            if payment.bukti_pembayaran:
                old_file_path = get_upload_path(payment.bukti_pembayaran)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Save new payment proof file
            filename = save_payment_proof(
                form.bukti_pembayaran.data,
                payment.registration.user_id,
                payment.registration.competition_id,
                payment.id
            )
            
            # Update payment record
            payment.bukti_pembayaran = filename
            payment.catatan_user = form.catatan.data
            payment.tanggal_upload = datetime.utcnow()
            payment.status = 'pending'  # Reset to pending for re-review
            
            db.session.commit()
            
            flash('Bukti pembayaran berhasil diperbarui! Menunggu verifikasi ulang.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Payment edit error: {str(e)}')
            flash('Terjadi kesalahan saat memperbarui bukti pembayaran.', 'error')
    
    return render_template('payment/edit.html', 
                         form=form, 
                         payment=payment)


@bp.route('/<int:id>/view')
@login_required
def view_proof(id):
    """View payment proof and status"""
    payment = Payment.query.get_or_404(id)
    
    # Check if user owns this payment or is admin
    if payment.registration.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak memiliki akses ke pembayaran ini.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('payment/view.html', payment=payment)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@profile_required
def delete_proof(id):
    """Delete payment proof (if allowed)"""
    payment = Payment.query.get_or_404(id)
    
    # Check if user owns this payment
    if payment.registration.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke pembayaran ini.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Check if payment can be modified
    if not payment.can_be_modified():
        flash('Bukti pembayaran ini tidak dapat dihapus.', 'warning')
        return redirect(url_for('payment.view_proof', id=id))
    
    try:
        # Delete file if exists
        if payment.bukti_pembayaran:
            file_path = get_upload_path(payment.bukti_pembayaran)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Clear payment proof data
        payment.bukti_pembayaran = None
        payment.catatan_user = None
        payment.tanggal_upload = None
        
        db.session.commit()
        
        flash('Bukti pembayaran berhasil dihapus.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Payment delete error: {str(e)}')
        flash('Terjadi kesalahan saat menghapus bukti pembayaran.', 'error')
    
    return redirect(url_for('payment.upload_proof', id=id))


@bp.route('/file/<path:filename>')
def uploaded_file(filename):
    """Serve payment proof files"""
    # Security check - only allow access to own files or admin
    if not current_user.is_authenticated:
        return redirect(url_for('auth.masuk'))
    
    # Extract payment ID from filename to check ownership
    try:
        # Assuming filename format: payment_proof_<user_id>_<competition_id>_<payment_id>_<timestamp>.<ext>
        parts = filename.split('_')
        if len(parts) >= 4 and parts[0] == 'payment' and parts[1] == 'proof':
            user_id = int(parts[2])
            payment_id = int(parts[4])
            
            # Check if user owns this file or is admin
            if current_user.id != user_id and not current_user.is_admin:
                flash('Akses ditolak.', 'error')
                return redirect(url_for('main.dashboard'))
    except (ValueError, IndexError):
        if not current_user.is_admin:
            flash('Akses ditolak.', 'error')
            return redirect(url_for('main.dashboard'))
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/uploads')
    return send_from_directory(upload_folder, filename)


@bp.route('/<int:id>/status')
@login_required
def payment_status(id):
    """Get payment status (AJAX endpoint)"""
    payment = Payment.query.get_or_404(id)
    
    # Check if user owns this payment
    if payment.registration.user_id != current_user.id:
        return {'error': 'Access denied'}, 403
    
    return {
        'success': True,
        'payment': {
            'id': payment.id,
            'status': payment.status,
            'status_display': payment.get_status_display(),
            'amount': payment.jumlah,
            'amount_formatted': payment.get_amount_display(),
            'has_proof': bool(payment.bukti_pembayaran),
            'upload_deadline': payment.get_upload_deadline().isoformat() if payment.get_upload_deadline() else None,
            'time_left': payment.get_time_left_display(),
            'can_be_modified': payment.can_be_modified(),
            'is_deadline_passed': payment.is_upload_deadline_passed()
        }
    }