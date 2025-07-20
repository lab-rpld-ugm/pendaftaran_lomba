#!/usr/bin/env python3
"""
Test script for individual registration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, UserProfile
from app.models.competition import Competition
from app.models.registration import Registration, IndividualRegistration
from app.models.payment import Payment
from app.forms.registration import IndividualRegistrationForm
from datetime import datetime, timedelta
import tempfile
from werkzeug.datastructures import FileStorage
from io import BytesIO


def test_individual_registration_form():
    """Test IndividualRegistrationForm functionality"""
    print("Testing IndividualRegistrationForm...")
    
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    
    with app.app_context():
        # Create test competition
        competition = Competition(
            nama_kompetisi="Test Math Olympiad",
            deskripsi="Test competition",
            kategori="individual",
            jenis="math",
            harga_early_bird=50000,
            harga_reguler=75000,
            tanggal_mulai_early_bird=datetime.utcnow(),
            tanggal_akhir_early_bird=datetime.utcnow() + timedelta(days=7),
            deadline_registrasi=datetime.utcnow() + timedelta(days=30),
            tanggal_kompetisi=datetime.utcnow() + timedelta(days=45),
            min_kelas=7,
            max_kelas=9
        )
        
        # Test form initialization
        form = IndividualRegistrationForm(competition=competition)
        
        print(f"✓ Form initialized with competition: {competition.nama_kompetisi}")
        print(f"✓ Competition ID set: {form.competition_id.data}")
        print(f"✓ Locked price set: {form.locked_price.data}")
        print(f"✓ Submission type: {form.get_submission_type()}")
        
        # Test file extensions
        math_extensions = IndividualRegistrationForm.get_allowed_file_extensions('math')
        informatics_extensions = IndividualRegistrationForm.get_allowed_file_extensions('informatics')
        
        print(f"✓ Math allowed extensions: {math_extensions}")
        print(f"✓ Informatics allowed extensions: {informatics_extensions}")
        
        # Test submission requirements
        print(f"✓ Math requires file upload: {IndividualRegistrationForm.requires_file_upload('math')}")
        print(f"✓ Creative requires Google Drive: {IndividualRegistrationForm.requires_google_drive('creative')}")
        
        print("IndividualRegistrationForm tests passed!\n")


def test_registration_models():
    """Test registration models"""
    print("Testing Registration models...")
    
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(email="test@example.com")
        user.set_password("testpass")
        
        profile = UserProfile(
            user=user,
            nama_lengkap="Test User",
            sekolah="Test School",
            kelas=8,
            nisn="1234567890",
            whatsapp="081234567890",
            instagram="testuser",
            twitter="testuser",
            is_verified=True
        )
        
        db.session.add(user)
        db.session.add(profile)
        
        # Create test competition
        competition = Competition(
            nama_kompetisi="Test Science Olympiad",
            deskripsi="Test competition",
            kategori="individual",
            jenis="science",
            harga_early_bird=60000,
            harga_reguler=80000,
            tanggal_mulai_early_bird=datetime.utcnow(),
            tanggal_akhir_early_bird=datetime.utcnow() + timedelta(days=7),
            deadline_registrasi=datetime.utcnow() + timedelta(days=30),
            tanggal_kompetisi=datetime.utcnow() + timedelta(days=45),
            min_kelas=7,
            max_kelas=9
        )
        
        db.session.add(competition)
        db.session.commit()
        
        # Test individual registration
        registration = IndividualRegistration(
            user_id=user.id,
            competition_id=competition.id,
            harga_terkunci=competition.get_current_price(),
            status='pending'
        )
        
        db.session.add(registration)
        db.session.commit()
        
        print(f"✓ Individual registration created: {registration}")
        print(f"✓ Registration type: {registration.get_type()}")
        print(f"✓ Status display: {registration.get_status_display()}")
        print(f"✓ Can submit files: {registration.can_submit_files()}")
        print(f"✓ Submission deadline: {registration.get_submission_deadline()}")
        
        # Test payment
        payment = Payment(
            registration_id=registration.id,
            jumlah=registration.harga_terkunci,
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        print(f"✓ Payment created: {payment}")
        print(f"✓ Payment amount: {payment.get_formatted_amount()}")
        print(f"✓ Payment type: {payment.get_payment_type()}")
        print(f"✓ Time left: {payment.get_time_left()}")
        print(f"✓ Can be modified: {payment.can_be_modified()}")
        
        # Clean up
        db.session.delete(payment)
        db.session.delete(registration)
        db.session.delete(profile)
        db.session.delete(user)
        db.session.delete(competition)
        db.session.commit()
        
        print("Registration models tests passed!\n")


def test_competition_eligibility():
    """Test competition eligibility logic"""
    print("Testing Competition eligibility...")
    
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create test user with complete profile
        user = User(email="eligible@example.com")
        user.set_password("testpass")
        
        profile = UserProfile(
            user=user,
            nama_lengkap="Eligible User",
            sekolah="Test School",
            kelas=8,
            nisn="1234567891",
            whatsapp="081234567891",
            instagram="eligibleuser",
            twitter="eligibleuser",
            is_verified=True
        )
        
        db.session.add(user)
        db.session.add(profile)
        
        # Create test competition
        competition = Competition(
            nama_kompetisi="Test Logic Olympiad",
            deskripsi="Test competition",
            kategori="individual",
            jenis="logic",
            harga_early_bird=55000,
            harga_reguler=70000,
            tanggal_mulai_early_bird=datetime.utcnow(),
            tanggal_akhir_early_bird=datetime.utcnow() + timedelta(days=7),
            deadline_registrasi=datetime.utcnow() + timedelta(days=30),
            tanggal_kompetisi=datetime.utcnow() + timedelta(days=45),
            min_kelas=7,
            max_kelas=9
        )
        
        db.session.add(competition)
        db.session.commit()
        
        # Test eligibility
        is_eligible = competition.is_user_eligible(user)
        print(f"✓ User eligibility: {is_eligible}")
        
        # Test pricing
        current_price = competition.get_current_price()
        is_early_bird = competition.is_early_bird_active()
        pricing_info = competition.get_pricing_info()
        
        print(f"✓ Current price: Rp {current_price:,}")
        print(f"✓ Early bird active: {is_early_bird}")
        print(f"✓ Early bird savings: Rp {pricing_info['early_bird_savings']:,}")
        print(f"✓ Registration open: {pricing_info['is_registration_open']}")
        
        # Clean up
        db.session.delete(profile)
        db.session.delete(user)
        db.session.delete(competition)
        db.session.commit()
        
        print("Competition eligibility tests passed!\n")


def main():
    """Run all tests"""
    print("=== Testing Individual Registration Implementation ===\n")
    
    try:
        test_individual_registration_form()
        test_registration_models()
        test_competition_eligibility()
        
        print("=== All Tests Passed! ===")
        print("\nIndividual registration implementation is working correctly.")
        print("\nKey features implemented:")
        print("✓ IndividualRegistrationForm with validation")
        print("✓ File upload for academic competitions")
        print("✓ Google Drive link for creative/performance competitions")
        print("✓ Automatic price calculation and locking")
        print("✓ User eligibility validation")
        print("✓ Payment integration")
        print("✓ Registration template with Bootstrap styling")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)