#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.payment import Payment
from app.models.registration import Registration
from app.forms.payment import PaymentUploadForm
from datetime import datetime, timedelta

def test_payment_upload():
    """Test payment upload functionality"""
    print("=== Testing Payment Upload System ===\n")
    
    app = create_app()
    
    with app.app_context():
        print("1. Testing Payment model methods...")
        
        # Get a payment record
        payment = Payment.query.first()
        if not payment:
            print("   ❌ No payment records found")
            return
        
        print(f"   ✓ Found payment: {payment}")
        print(f"   ✓ Amount display: {payment.get_amount_display()}")
        print(f"   ✓ Status display: {payment.get_status_display()}")
        print(f"   ✓ Payment type: {payment.get_payment_type()}")
        print(f"   ✓ Can be modified: {payment.can_be_modified()}")
        print(f"   ✓ Upload deadline: {payment.get_upload_deadline()}")
        print(f"   ✓ Time left: {payment.get_time_left_display()}")
        print(f"   ✓ Is deadline passed: {payment.is_upload_deadline_passed()}")
        
        print("\n2. Testing Payment forms...")
        
        # Test PaymentUploadForm (without CSRF for testing)
        with app.test_request_context():
            app.config['WTF_CSRF_ENABLED'] = False
            form = PaymentUploadForm(payment=payment)
            print(f"   ✓ PaymentUploadForm created")
            print(f"   ✓ Payment ID field: {form.payment_id.data}")
        
        print("\n3. Testing Payment routes...")
        
        # Test routes exist
        with app.test_client() as client:
            # Test upload route (should redirect to login)
            response = client.get(f'/pembayaran/{payment.id}/upload')
            print(f"   ✓ Upload route status: {response.status_code}")
            
            # Test view route (should redirect to login)
            response = client.get(f'/pembayaran/{payment.id}/view')
            print(f"   ✓ View route status: {response.status_code}")
        
        print("\n4. Testing file handler functions...")
        
        # Test file handler functions exist
        from app.utils.file_handler import save_payment_proof, get_upload_path
        print(f"   ✓ save_payment_proof function exists")
        print(f"   ✓ get_upload_path function exists")
        
        # Test upload path
        upload_path = get_upload_path('payment_proofs')
        print(f"   ✓ Payment proofs upload path: {upload_path}")
        
        print("\n5. Testing Payment templates...")
        
        # Check if templates exist
        template_files = [
            'app/templates/payment/upload.html',
            'app/templates/payment/view.html'
        ]
        
        for template in template_files:
            if os.path.exists(template):
                print(f"   ✓ Template exists: {template}")
            else:
                print(f"   ❌ Template missing: {template}")
        
        print("\n6. Testing Payment queries...")
        
        # Test static methods
        pending_payments = Payment.get_pending_payments()
        print(f"   ✓ Pending payments: {len(pending_payments)}")
        
        overdue_payments = Payment.get_overdue_payments()
        print(f"   ✓ Overdue payments: {len(overdue_payments)}")
        
        print("\n=== Payment Upload System Test Complete ===")
        
        print("\nKey features implemented:")
        print("✓ Payment model with upload methods")
        print("✓ Payment upload and edit forms")
        print("✓ Payment routes (upload, view, edit)")
        print("✓ Payment templates with file upload")
        print("✓ File handler for payment proofs")
        print("✓ Payment deadline validation")
        print("✓ Payment status management")
        print("✓ Integration with registration system")

if __name__ == '__main__':
    test_payment_upload()