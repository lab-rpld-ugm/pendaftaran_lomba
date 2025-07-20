from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from app import db


class Payment(db.Model):
    """Payment model for competition registrations"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    
    # Payment information
    jumlah = db.Column(db.Integer, nullable=False)  # Amount in rupiah
    bukti_pembayaran = db.Column(db.String(200))  # Payment proof file path
    catatan_user = db.Column(db.Text)  # User notes when uploading proof
    
    # Payment status
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected
    
    # Admin information
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_notes = db.Column(db.Text)  # Admin notes for approval/rejection
    catatan_admin = db.Column(db.Text)  # Admin notes for user
    
    # Timestamps
    tanggal_upload = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_approval = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment {self.id}: {self.jumlah} - {self.status}>'
    
    def calculate_amount(self):
        """Calculate payment amount based on registration"""
        if not self.registration:
            return 0
        
        # For individual registrations, use locked price
        if self.registration.get_type() == 'individual':
            return self.registration.harga_terkunci
        
        # For team registrations, calculate based on team size
        if self.registration.team:
            team = self.registration.team
            member_count = team.get_member_count()
            return self.registration.harga_terkunci * member_count
        
        return self.registration.harga_terkunci
    
    def is_within_deadline(self):
        """Check if payment is within 24-hour deadline"""
        if not self.registration:
            return False
        
        deadline = self.registration.tanggal_registrasi + timedelta(hours=24)
        return datetime.utcnow() <= deadline
    
    def get_deadline(self):
        """Get payment deadline (24 hours after registration)"""
        if not self.registration:
            return None
        
        return self.registration.tanggal_registrasi + timedelta(hours=24)
    
    def is_overdue(self):
        """Check if payment is overdue"""
        deadline = self.get_deadline()
        if not deadline:
            return False
        
        return datetime.utcnow() > deadline
    
    def approve_payment(self, admin_user_id, notes=None):
        """Approve the payment"""
        self.status = 'approved'
        self.approved_by = admin_user_id
        self.tanggal_approval = datetime.utcnow()
        
        if notes:
            self.admin_notes = notes
        
        # Also approve the associated registration
        if self.registration:
            self.registration.approve_registration(admin_user_id)
        
        db.session.commit()
        
        return True, "Pembayaran berhasil disetujui"
    
    def reject_payment(self, admin_user_id, notes=None):
        """Reject the payment"""
        self.status = 'rejected'
        self.approved_by = admin_user_id
        
        if notes:
            self.admin_notes = notes
        
        # Also reject the associated registration
        if self.registration:
            self.registration.reject_registration(admin_user_id)
        
        db.session.commit()
        
        return True, "Pembayaran ditolak"
    
    def get_status_display(self):
        """Get human-readable status"""
        status_mapping = {
            'pending': 'Menunggu Verifikasi',
            'approved': 'Disetujui',
            'rejected': 'Ditolak'
        }
        return status_mapping.get(self.status, self.status.title())
    
    def get_formatted_amount(self):
        """Get formatted amount in rupiah"""
        return f"Rp {self.jumlah:,}".replace(',', '.')
    
    def get_time_left(self):
        """Get time left until deadline"""
        deadline = self.get_deadline()
        if not deadline:
            return None
        
        if self.is_overdue():
            return "Terlambat"
        
        time_left = deadline - datetime.utcnow()
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours} jam {minutes} menit"
        else:
            return f"{minutes} menit"
    
    def can_be_modified(self):
        """Check if payment can still be modified"""
        return self.status == 'pending' and not self.is_overdue()
    
    def get_payment_type(self):
        """Get payment type based on registration"""
        if not self.registration:
            return "Unknown"
        
        if self.registration.get_type() == 'individual':
            return "Individu"
        else:
            return "Tim"
    
    def validate_amount(self):
        """Validate if payment amount matches expected amount"""
        expected_amount = self.calculate_amount()
        return self.jumlah == expected_amount
    
    @staticmethod
    def get_pending_payments():
        """Get all pending payments for admin review"""
        return Payment.query.filter_by(status='pending').order_by(Payment.tanggal_upload.desc()).all()
    
    @staticmethod
    def get_overdue_payments():
        """Get all overdue payments"""
        from app.models.registration import Registration
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        return db.session.query(Payment).join(Registration).filter(
            Payment.status == 'pending',
            Registration.tanggal_registrasi < cutoff_time
        ).all()
    
    @staticmethod
    def cleanup_overdue_payments():
        """Mark overdue payments as rejected"""
        overdue_payments = Payment.get_overdue_payments()
        
        for payment in overdue_payments:
            payment.status = 'rejected'
            payment.admin_notes = 'Otomatis ditolak karena melewati batas waktu 24 jam'
            
            if payment.registration:
                payment.registration.status = 'rejected'
        
        db.session.commit()
        
        return len(overdue_payments)
    
    def get_amount_display(self):
        """Get formatted amount display"""
        return f"Rp {self.jumlah:,}"
    
    def get_upload_deadline(self):
        """Get upload deadline (24 hours after registration)"""
        if not self.registration:
            return None
        return self.registration.tanggal_registrasi + timedelta(hours=24)
    
    def is_upload_deadline_passed(self):
        """Check if upload deadline has passed"""
        deadline = self.get_upload_deadline()
        if not deadline:
            return False
        return datetime.utcnow() > deadline
    
    def get_time_left_display(self):
        """Get time left display for templates"""
        if self.is_upload_deadline_passed():
            return "Terlambat"
        
        deadline = self.get_upload_deadline()
        if not deadline:
            return "Tidak ada deadline"
        
        time_left = deadline - datetime.utcnow()
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours} jam {minutes} menit"
        else:
            return f"{minutes} menit"