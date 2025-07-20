#!/usr/bin/env python3
"""
Test script for profile verification system
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.user import User, UserProfile
from app.utils.verification import ProfileVerificationHelper, check_competition_eligibility

def test_verification_system():
    """Test profile verification system functionality"""
    app = create_app('testing')
    
    with app.app_context():
        # Create test user
        user = User(email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        
        print("Testing Profile Verification System...")
        
        # Test 1: User without profile
        print("\n1. Testing user without profile:")
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        print(f"   Status: {status_info['status']}")
        print(f"   Message: {status_info['message']}")
        print(f"   Can register: {status_info['can_register']}")
        print(f"   Completion: {status_info['completion_percentage']}%")
        
        # Test 2: User with incomplete profile
        print("\n2. Testing user with incomplete profile:")
        profile = UserProfile(user_id=user.id)
        profile.nama_lengkap = "John Doe"
        profile.sekolah = "SMP Test"
        profile.kelas = 8
        # Missing other fields
        db.session.add(profile)
        db.session.commit()
        
        completion = profile.calculate_completion_percentage()
        print(f"   Completion percentage: {completion}%")
        print(f"   Missing fields: {profile.get_missing_fields()}")
        
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        print(f"   Status: {status_info['status']}")
        print(f"   Can register: {status_info['can_register']}")
        
        # Test 3: User with complete profile but not verified
        print("\n3. Testing user with complete profile (not verified):")
        profile.nisn = "1234567890"
        profile.whatsapp = "081234567890"
        profile.instagram = "johndoe"
        profile.twitter = "johndoe"
        profile.foto_kartu_pelajar = "test_photo.jpg"
        profile.screenshot_twibbon = "test_twibbon.jpg"
        db.session.commit()
        
        completion = profile.calculate_completion_percentage()
        print(f"   Completion percentage: {completion}%")
        
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        print(f"   Status: {status_info['status']}")
        print(f"   Can register: {status_info['can_register']}")
        
        # Test 4: User with verified profile
        print("\n4. Testing user with verified profile:")
        profile.is_verified = True
        db.session.commit()
        
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        print(f"   Status: {status_info['status']}")
        print(f"   Can register: {status_info['can_register']}")
        
        # Test 5: Competition eligibility
        print("\n5. Testing competition eligibility:")
        can_register, reason = ProfileVerificationHelper.can_register_competition(user)
        print(f"   Can register for competition: {can_register}")
        print(f"   Reason: {reason}")
        
        # Test 6: Badge and icon classes
        print("\n6. Testing UI helper methods:")
        badge_class = ProfileVerificationHelper.get_verification_badge_class(user)
        icon = ProfileVerificationHelper.get_verification_icon(user)
        next_action = ProfileVerificationHelper.get_next_action_message(user)
        print(f"   Badge class: {badge_class}")
        print(f"   Icon: {icon}")
        print(f"   Next action: {next_action}")
        
        print("\n✓ Profile verification system tests completed successfully!")

if __name__ == '__main__':
    test_verification_system()