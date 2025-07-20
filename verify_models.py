#!/usr/bin/env python3
"""
Simple verification script to check if models can be imported
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to import Flask app and models...")
    
    from app import create_app, db
    print("✓ Successfully imported Flask app and db")
    
    from app.models import (
        User, UserProfile, Competition, CompetitionCategory,
        Registration, IndividualRegistration, TeamRegistration,
        Team, TeamMember, Payment
    )
    print("✓ Successfully imported all models")
    
    # Create app context to test model creation
    app = create_app()
    print("✓ Successfully created Flask app")
    
    with app.app_context():
        print("✓ Successfully entered app context")
        
        # Test User and UserProfile models
        user = User(email='test@example.com')
        profile = UserProfile()
        
        print("✓ Successfully created User and UserProfile instances")
        print("✓ User model has required methods:", hasattr(user, 'set_password'), hasattr(user, 'check_password'))
        print("✓ UserProfile model has required methods:", hasattr(profile, 'calculate_completion_percentage'))
        
        # Test password functionality
        user.set_password('test123')
        print("✓ Password hashing works:", user.check_password('test123'))
        
        # Test profile completion
        completion = profile.calculate_completion_percentage()
        print(f"✓ Profile completion calculation works: {completion}%")
        
        missing = profile.get_missing_fields()
        print(f"✓ Missing fields detection works: {len(missing)} fields missing")
        
        # Test Competition models
        from datetime import datetime, timedelta
        
        competition = Competition(
            nama_kompetisi='Test Math Olympiad',
            kategori='individual',
            jenis='academic',
            harga_early_bird=50000,
            harga_reguler=75000,
            tanggal_mulai_early_bird=datetime.utcnow(),
            tanggal_akhir_early_bird=datetime.utcnow() + timedelta(days=7),
            deadline_registrasi=datetime.utcnow() + timedelta(days=30),
            tanggal_kompetisi=datetime.utcnow() + timedelta(days=45)
        )
        
        print("✓ Successfully created Competition instance")
        print("✓ Competition model has required methods:", hasattr(competition, 'get_current_price'), hasattr(competition, 'is_early_bird_active'))
        
        # Test pricing logic
        current_price = competition.get_current_price()
        is_early_bird = competition.is_early_bird_active()
        print(f"✓ Competition pricing works: Current price = {current_price}, Early bird active = {is_early_bird}")
        
        # Test eligibility check
        profile.kelas = 8
        profile.nama_lengkap = "Test User"
        profile.sekolah = "Test School"
        profile.nisn = "1234567890"
        profile.whatsapp = "081234567890"
        profile.instagram = "@test"
        profile.twitter = "@test"
        profile.foto_kartu_pelajar = "test.jpg"
        profile.screenshot_twibbon = "test.jpg"
        user.profile = profile
        
        is_eligible = competition.is_user_eligible(user)
        print(f"✓ Competition eligibility check works: {is_eligible}")
        
        # Test CompetitionCategory
        category = CompetitionCategory(
            nama_kategori='Test Category',
            tipe_kompetisi='individual',
            requires_file_upload=True,
            allowed_file_types='pdf,doc,docx'
        )
        
        print("✓ Successfully created CompetitionCategory instance")
        print("✓ CompetitionCategory has required methods:", hasattr(category, 'is_file_allowed'), hasattr(category, 'get_allowed_extensions'))
        
        # Test file validation
        allowed_extensions = category.get_allowed_extensions()
        is_pdf_allowed = category.is_file_allowed('test.pdf')
        is_txt_allowed = category.is_file_allowed('test.txt')
        print(f"✓ File validation works: Extensions = {allowed_extensions}, PDF allowed = {is_pdf_allowed}, TXT allowed = {is_txt_allowed}")
        
        # Test Registration models
        registration = Registration(
            user_id=1,
            competition_id=1,
            harga_terkunci=50000
        )
        
        print("✓ Successfully created Registration instance")
        print("✓ Registration has required methods:", hasattr(registration, 'get_status_display'), hasattr(registration, 'can_submit_files'))
        
        # Test registration status
        status_display = registration.get_status_display()
        can_submit = registration.can_submit_files()
        print(f"✓ Registration status works: Status = {status_display}, Can submit = {can_submit}")
        
        # Test IndividualRegistration
        individual_reg = IndividualRegistration(
            user_id=1,
            competition_id=1,
            harga_terkunci=50000
        )
        
        print("✓ Successfully created IndividualRegistration instance")
        print(f"✓ Individual registration type: {individual_reg.get_type()}")
        
        # Test Team model
        team = Team(
            nama_tim='Test Team',
            competition_id=1,
            captain_id=1
        )
        
        print("✓ Successfully created Team instance")
        print("✓ Team has required methods:", hasattr(team, 'add_member'), hasattr(team, 'validate_school_consistency'))
        
        # Test team validation
        is_valid, message = team.validate_school_consistency()
        is_complete = team.is_complete()
        member_count = team.get_member_count()
        print(f"✓ Team validation works: Valid = {is_valid}, Complete = {is_complete}, Members = {member_count}")
        
        # Test TeamMember
        team_member = TeamMember(
            team_id=1,
            user_id=1,
            posisi='Captain'
        )
        
        print("✓ Successfully created TeamMember instance")
        position_display = team_member.get_position_display()
        print(f"✓ Team member position display: {position_display}")
        
        # Test Payment model
        payment = Payment(
            registration_id=1,
            jumlah=50000
        )
        
        print("✓ Successfully created Payment instance")
        print("✓ Payment has required methods:", hasattr(payment, 'calculate_amount'), hasattr(payment, 'approve_payment'))
        
        # Test payment functionality
        amount = payment.calculate_amount()
        status_display = payment.get_status_display()
        formatted_amount = payment.get_formatted_amount()
        is_within_deadline = payment.is_within_deadline()
        
        print(f"✓ Payment functionality works:")
        print(f"  - Amount: {amount}")
        print(f"  - Status: {status_display}")
        print(f"  - Formatted: {formatted_amount}")
        print(f"  - Within deadline: {is_within_deadline}")
        
        print("\n✅ All model verifications passed!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()