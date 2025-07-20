#!/usr/bin/env python3
"""
Test script to verify Competition and CompetitionCategory models work correctly
"""
import os
import sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, UserProfile, Competition, CompetitionCategory

def test_competition_model():
    """Test Competition model functionality"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Test Competition creation
        now = datetime.utcnow()
        competition = Competition(
            nama_kompetisi='Test Math Olympiad',
            kategori='individual',
            jenis='academic',
            harga_early_bird=50000,
            harga_reguler=75000,
            tanggal_mulai_early_bird=now,
            tanggal_akhir_early_bird=now + timedelta(days=7),
            deadline_registrasi=now + timedelta(days=30),
            tanggal_kompetisi=now + timedelta(days=45)
        )
        
        print("✓ Competition model created successfully")
        
        # Test get_current_price() method
        current_price = competition.get_current_price()
        assert current_price == 50000  # Should be early bird price
        print(f"✓ get_current_price() works: {current_price}")
        
        # Test is_early_bird_active() method
        is_early_bird = competition.is_early_bird_active()
        assert is_early_bird == True  # Should be active now
        print(f"✓ is_early_bird_active() works: {is_early_bird}")
        
        # Test get_participant_count() method
        participant_count = competition.get_participant_count()
        assert participant_count == 0  # No registrations yet
        print(f"✓ get_participant_count() works: {participant_count}")
        
        # Test user eligibility with complete profile
        user = User(email='test@example.com')
        user.set_password('testpassword')
        
        profile = UserProfile(
            user=user,
            nama_lengkap="Test User",
            sekolah="SMP Test",
            kelas=8,  # Valid grade
            nisn="1234567890",
            whatsapp="081234567890",
            instagram="@testuser",
            twitter="@testuser",
            foto_kartu_pelajar="test_id.jpg",
            screenshot_twibbon="test_twibbon.jpg"
        )
        
        # Save to database
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        
        # Test is_user_eligible() method
        is_eligible = competition.is_user_eligible(user)
        assert is_eligible == True  # User should be eligible
        print(f"✓ is_user_eligible() works: {is_eligible}")
        
        # Test grade eligibility validation
        profile.kelas = 6  # Below minimum
        is_eligible_low = competition.is_user_eligible(user)
        assert is_eligible_low == False
        
        profile.kelas = 10  # Above maximum
        is_eligible_high = competition.is_user_eligible(user)
        assert is_eligible_high == False
        
        profile.kelas = 7  # Valid grade
        is_eligible_valid = competition.is_user_eligible(user)
        assert is_eligible_valid == True
        
        print("✓ Grade eligibility validation (7, 8, 9) works correctly")
        
        # Test additional methods
        savings = competition.get_early_bird_savings()
        assert savings == 25000  # 75000 - 50000
        print(f"✓ get_early_bird_savings() works: {savings}")
        
        days_left = competition.get_early_bird_days_left()
        assert days_left >= 0
        print(f"✓ get_early_bird_days_left() works: {days_left}")
        
        is_open = competition.is_registration_open()
        assert is_open == True
        print(f"✓ is_registration_open() works: {is_open}")
        
        # Test expired early bird
        competition.tanggal_akhir_early_bird = now - timedelta(days=1)
        is_early_bird_expired = competition.is_early_bird_active()
        assert is_early_bird_expired == False
        
        current_price_regular = competition.get_current_price()
        assert current_price_regular == 75000  # Should be regular price
        print("✓ Early bird expiration works correctly")
        
        print("✓ All Competition model tests passed!")

def test_competition_category_model():
    """Test CompetitionCategory model functionality"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Test CompetitionCategory creation
        category = CompetitionCategory(
            nama_kategori='Math Olympiad',
            deskripsi='Olimpiade Matematika untuk siswa SMP',
            tipe_kompetisi='individual',
            requires_file_upload=True,
            allowed_file_types='pdf,doc,docx',
            max_file_size_mb=10
        )
        
        print("✓ CompetitionCategory model created successfully")
        
        # Test get_allowed_extensions() method
        extensions = category.get_allowed_extensions()
        assert extensions == ['pdf', 'doc', 'docx']
        print(f"✓ get_allowed_extensions() works: {extensions}")
        
        # Test is_file_allowed() method
        assert category.is_file_allowed('test.pdf') == True
        assert category.is_file_allowed('test.doc') == True
        assert category.is_file_allowed('test.txt') == False
        assert category.is_file_allowed('test') == False
        print("✓ is_file_allowed() works correctly")
        
        # Test get_submission_requirements() method
        requirements = category.get_submission_requirements()
        expected = {
            'file_upload': True,
            'google_drive': False,
            'allowed_types': ['pdf', 'doc', 'docx'],
            'max_size_mb': 10
        }
        assert requirements == expected
        print("✓ get_submission_requirements() works correctly")
        
        # Test create_default_categories() method
        CompetitionCategory.create_default_categories()
        
        # Check if default categories were created
        math_category = CompetitionCategory.query.filter_by(nama_kategori='Math Olympiad').first()
        assert math_category is not None
        
        basketball_category = CompetitionCategory.query.filter_by(nama_kategori='Basketball').first()
        assert basketball_category is not None
        assert basketball_category.tipe_kompetisi == 'team'
        assert basketball_category.min_team_size == 5
        assert basketball_category.max_team_size == 8
        
        print("✓ create_default_categories() works correctly")
        print("✓ All CompetitionCategory model tests passed!")

if __name__ == '__main__':
    print("Testing Competition and CompetitionCategory models...")
    test_competition_model()
    test_competition_category_model()
    print("\n✅ All tests passed successfully!")