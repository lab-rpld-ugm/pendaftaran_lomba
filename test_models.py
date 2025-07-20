#!/usr/bin/env python3
"""
Test script to verify User and UserProfile models work correctly
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, UserProfile

def test_user_model():
    """Test User model functionality"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Test user creation
        user = User(email='test@example.com')
        user.set_password('testpassword')
        
        # Test password checking
        assert user.check_password('testpassword') == True
        assert user.check_password('wrongpassword') == False
        
        # Test profile completion (should be False without profile)
        assert user.is_profile_complete() == False
        assert user.get_verification_progress() == 0
        
        # Save user to database
        db.session.add(user)
        db.session.commit()
        
        print("✓ User model tests passed")
        
        # Test UserProfile
        profile = UserProfile(user_id=user.id)
        
        # Test empty profile completion
        assert profile.calculate_completion_percentage() == 0
        assert len(profile.get_missing_fields()) == 9
        
        # Fill some fields
        profile.nama_lengkap = "Test User"
        profile.sekolah = "SMP Test"
        profile.kelas = 8
        
        # Test partial completion
        completion = profile.calculate_completion_percentage()
        assert completion > 0 and completion < 100
        
        # Fill all required fields
        profile.nisn = "1234567890"
        profile.whatsapp = "081234567890"
        profile.instagram = "@testuser"
        profile.twitter = "@testuser"
        profile.foto_kartu_pelajar = "test_id.jpg"
        profile.screenshot_twibbon = "test_twibbon.jpg"
        
        # Test complete profile
        assert profile.calculate_completion_percentage() == 100
        assert len(profile.get_missing_fields()) == 0
        assert profile.is_grade_eligible() == True
        
        # Save profile
        db.session.add(profile)
        db.session.commit()
        
        # Test user with complete profile
        assert user.is_profile_complete() == True
        assert user.get_verification_progress() == 100
        
        print("✓ UserProfile model tests passed")
        
        # Test grade eligibility
        profile.kelas = 6  # Below minimum
        assert profile.is_grade_eligible() == False
        
        profile.kelas = 10  # Above maximum
        assert profile.is_grade_eligible() == False
        
        profile.kelas = 8  # Within range
        assert profile.is_grade_eligible() == True
        
        print("✓ Grade eligibility tests passed")
        
        # Clean up
        db.session.delete(profile)
        db.session.delete(user)
        db.session.commit()
        
        print("✓ All User and UserProfile model tests passed!")

if __name__ == '__main__':
    test_user_model()