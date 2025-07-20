from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import HiddenField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from app.models.payment import Payment


class PaymentUploadForm(FlaskForm):
    """Form for uploading payment proof"""
    bukti_pembayaran = FileField('Bukti Pembayaran', validators=[
        FileRequired(message='File bukti pembayaran harus diupload'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 
                   message='Hanya file JPG, PNG, atau PDF yang diizinkan')
    ])
    
    catatan = TextAreaField('Catatan (Opsional)', validators=[
        Optional(),
        Length(max=500, message='Catatan maksimal 500 karakter')
    ])
    
    payment_id = HiddenField('Payment ID', validators=[DataRequired()])
    
    submit = SubmitField('Upload Bukti Pembayaran')
    
    def __init__(self, payment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payment = payment
        if payment:
            self.payment_id.data = payment.id
    
    def validate_payment_id(self, field):
        """Validate payment exists and is pending"""
        from wtforms.validators import ValidationError
        
        payment = Payment.query.get(field.data)
        if not payment:
            raise ValidationError('Pembayaran tidak ditemukan')
        
        if payment.status != 'pending':
            raise ValidationError('Pembayaran sudah diproses')
        
        if payment.bukti_pembayaran:
            raise ValidationError('Bukti pembayaran sudah diupload')


class PaymentEditForm(FlaskForm):
    """Form for editing payment proof (if allowed)"""
    bukti_pembayaran = FileField('Bukti Pembayaran Baru', validators=[
        FileRequired(message='File bukti pembayaran harus diupload'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 
                   message='Hanya file JPG, PNG, atau PDF yang diizinkan')
    ])
    
    catatan = TextAreaField('Catatan Perubahan', validators=[
        DataRequired(message='Catatan perubahan harus diisi'),
        Length(min=10, max=500, message='Catatan harus antara 10-500 karakter')
    ])
    
    payment_id = HiddenField('Payment ID', validators=[DataRequired()])
    
    submit = SubmitField('Update Bukti Pembayaran')
    
    def __init__(self, payment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payment = payment
        if payment:
            self.payment_id.data = payment.id
    
    def validate_payment_id(self, field):
        """Validate payment can be edited"""
        from wtforms.validators import ValidationError
        
        payment = Payment.query.get(field.data)
        if not payment:
            raise ValidationError('Pembayaran tidak ditemukan')
        
        if payment.status == 'approved':
            raise ValidationError('Pembayaran yang sudah disetujui tidak dapat diubah')
        
        if payment.status == 'rejected' and not payment.can_be_modified():
            raise ValidationError('Pembayaran ini tidak dapat diubah lagi')